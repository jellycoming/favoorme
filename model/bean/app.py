# coding=utf-8
from sqlalchemy import Column, Integer, String
from model.bean import Base


class App(Base):
    __tablename__ = 'entity_app'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    ctime = Column('ctime', String)


class IOSApp(Base):
    __tablename__ = 'entity_iosapp'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    appid = Column('appid', String)
    appname = Column('appname', String)
    ctime = Column('ctime', String)