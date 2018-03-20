# coding=utf-8
import tornado.web
import tornado.gen
from lib.exception import BadRequest
from handler.base import Basehandler, Response
from handler.api import BaseApi
from model.items import App
from model.dao.app import AppDao
from lib.util import randkey


class AppHandler(Basehandler):
    """
    GET: 获取app,如果未指定appid,则获取所有
    POST: 如果指定appid,修改或删除(post data为空则删除);未指定appid,则添加
    """
    def get(self, appid=None):
        if appid is not None:
            with self.db as db:
                res = db.execute(App.retrieve(appid=appid))
                rv = res.all if appid is None else res.one
            self.write(Response(data=rv))
        else:
            with self.dbsession as dbsession:
                dao = AppDao(dbsession=dbsession)
                dao.update(appid=appid, name='hello')
                app = dao.retrieve_one(appid=appid)
                self.write(app.name)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self, appid=None):
        with self.db as db:
            if appid is None:
                app = App(appkey=randkey(), **self.data)
                res = db.execute(App.create(app=app))
                app.id = res.lastrowid
                rv = yield self.http_client.fetch(BaseApi(url='http://127.0.0.1/api'))
            else:
                _app = db.execute(App.retrieve(appid=appid)).one
                if not _app:
                    raise BadRequest(description='app not found')
                if self.data:
                    app = App(id=appid, appkey=_app.appkey, **self.data)
                    db.execute(App.updated(app=app))
                else:
                    db.execute(App.delete(appid=appid))
        self.write(Response())