# coding=utf-8
from model.dao import BaseDao
from model.bean.app import App, IOSApp


class AppDao(BaseDao):
    def __init__(self, dbsession):
        self.dbsession = dbsession
        super(AppDao, self).__init__()

    def retrieve_all(self, appid):
        return self.dbsession.query(App, IOSApp).outerjoin(IOSApp, App.id == IOSApp.appid) \
            .filter(App.id == appid).all()

    def retrieve_one(self, appid):
        return self.dbsession.query(App).filter(App.id == appid).first()

    def update(self, appid, name):
        return self.dbsession.query(App).filter(App.id == appid).update({App.name: name})
