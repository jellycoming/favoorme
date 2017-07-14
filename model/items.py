# coding=utf-8
from lib.mysql import Executable
from model.base import BaseModel


class App(BaseModel):
    def __init__(self, **kwargs):
        super(App, self).__init__(**kwargs)

    @classmethod
    def create(cls, app):
        sql = 'insert into app(name,url,appkey,icon,platformid,areaid,companyid,biappid)values(?,?,?,?,?,?,?,?)'
        condition = (app.name, app.url, app.appkey, app.icon, app.platformid, app.areaid, app.companyid, app.biappid)
        return Executable(cls, sql, condition)

    @classmethod
    def updated(cls, app):
        sql = 'update app set name=?,url=?,icon=?,platformid=?,areaid=?,companyid=?,biappid=? where id=?'
        condition = (app.name, app.url, app.icon, app.platformid, app.areaid, app.companyid, app.biappid, app.id)
        return Executable(cls, sql, condition)

    @classmethod
    def retrieve(cls, appid=None):
        if appid is None:
            sql = 'select id,name,url,appkey,icon,platformid,areaid,biappid from app'
            return Executable(cls, sql)
        else:
            sql = 'select id,name,url,appkey,icon,platformid,areaid,biappid from app where id=?'
            return Executable(cls, sql, (appid,))

    @classmethod
    def delete(cls, appid):
        return Executable(cls, sql='delete from app where id=?', condition=(appid,))