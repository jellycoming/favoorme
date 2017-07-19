# coding=utf-8
import MySQLdb
import time
from threading import Condition


class DBConnectionPool(object):
    def __init__(self, init_idle_connections=1, max_idle_connections=0, max_open_connections=0, expired=3600, **kwargs):
        """
        :param int init_idle_connections: 初始化空闲连接数
        :param int max_idle_connections: 最大空闲连接数, 默认0为无限制
        :param int max_open_connections: 最大打开连接数, 默认0为无限制
        :param int expired: 连接的过期时间(秒)
        :param kwargs: 数据库连接参数
        """
        self._init_idle_connections = init_idle_connections
        self._max_idle_connections = max_idle_connections
        self._max_open_connections = max_open_connections
        self._expired = expired
        self._kwargs = kwargs
        self._idle_connections = []
        self._opened_connections = 0
        self._lock = Condition()
        connections = [self.connection() for _ in range(self._init_idle_connections)]
        while connections:
            connections.pop().close()

    def connection(self):
        self._lock.acquire()
        try:
            while self._max_open_connections and self._opened_connections >= self._max_open_connections:
                self._lock.wait()
            try:
                conn = self._idle_connections.pop(0)
            except IndexError:
                conn = MySQLdb.connect(**self._kwargs)
            else:
                conn.ping(True)
            conn = DBConnection(self, conn)
            self._opened_connections += 1
        finally:
            self._lock.release()
        return conn

    def cache(self, conn):
        self._lock.acquire()
        try:
            if (not self._max_idle_connections) or (len(self._idle_connections) < self._max_idle_connections):
                self._idle_connections.append(conn)
            else:
                conn.close()
            self._opened_connections -= 1
            self._lock.notify()
        finally:
            self._lock.release()

    def stat(self):
        self._lock.acquire()
        try:
            return 'opened connections:{}, free connections: {}'.format(self._opened_connections, len(self._idle_connections))
        finally:
            self._lock.release()


class DBConnection(object):
    def __init__(self, pool, conn):
        self._created_time = time.time()
        self._pool = pool
        self._conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()

    @property
    def created_time(self):
        return self._created_time

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._pool.cache(self._conn)
        self._conn = None

    def destroy(self):
        self._conn.close()
        self._conn = None

    # def query(self, sql, condition=tuple()):
    #     sql = sql.replace('?', '%s')
    #     cursor = self._conn.cursor()
    #     try:
    #         cursor.execute(sql, condition)
    #         # self.commit()
    #         columns = [desc[0] for desc in cursor.description]
    #         return [dict(zip(columns, records)) for records in cursor.fetchall()]
    #     finally:
    #         if cursor:
    #             cursor.close()

    # def execute(self, sql, condition=tuple()):
    #     sql = sql.replace('?', '%s')
    #     cursor = self._conn.cursor()
    #     try:
    #         cursor.execute(sql, condition)
    #         # self.commit()
    #         return cursor
    #     except Exception:
    #         self.rollback()
    #         raise
    #     finally:
    #         if cursor:
    #             cursor.close()
    #
    # def executemany(self, sql, conditions=tuple()):
    #     sql = sql.replace("?", "%s")
    #     cursor = self._conn.cursor()
    #     try:
    #         cursor.executemany(sql, conditions)
    #         # self.commit()
    #         return cursor
    #     except Exception:
    #         self.rollback()
    #         raise
    #     finally:
    #         if cursor:
    #             cursor.close()

    def execute(self, executable):
        cursor = self._conn.cursor()
        try:
            cursor.execute(executable.sql.replace('?', '%s'), executable.condition)
            # self.commit()
            try:
                key = [desc[0] for desc in cursor.description]
                records = [dict(zip(key, val)) for val in cursor.fetchall()]
                rv = [executable.model_cls(**r) for r in records]
            except TypeError:
                rv = None  # cursor.description is None means not select sql, raise TypeError: 'NoneType' object is not iterable
            return Result(rv=rv, lastrowid=cursor.lastrowid, rowcount=cursor.rowcount)
        except Exception as e:
            self.rollback()
            # IntegrityError(1062, "Duplicate entry ... for key ...")
            # IntegrityError(1062, "Duplicate entry ... for key ...")
            code, msg = e
            if code == 1062:
                msg = '记录已存在!'
            raise Exception(msg)
        finally:
            if cursor:
                cursor.close()

    def executemany(self, executable):
        cursor = self._conn.cursor()
        try:
            cursor.executemany(executable.sql.replace('?', '%s'), executable.condition)
            # self.commit()
            return Result(rowcount=cursor.rowcount)
        except Exception:
            self.rollback()
            raise
        finally:
            if cursor:
                cursor.close()


class Executable(object):
    def __init__(self, model_cls, sql, condition=tuple()):
        self._model_cls = model_cls
        self._sql = sql
        self._condition = condition

    @property
    def model_cls(self):
        return self._model_cls

    @property
    def sql(self):
        return self._sql

    @property
    def condition(self):
        return self._condition


class Result(object):
    def __init__(self, rv=None, lastrowid=0, rowcount=0):
        self._rv = rv
        self._lastrowid = lastrowid
        self._rowcount = rowcount

    @property
    def all(self):
        return self._rv

    @property
    def one(self):
        return self._rv[0] if self._rv else None

    @property
    def lastrowid(self):
        return self._lastrowid

    @property
    def rowcount(self):
        return self._rowcount