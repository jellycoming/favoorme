# coding=utf-8
import os
import logging
import tornado.web
from lib.mysql import DBConnectionPool
from setting.mysql import MYSQLCONF
from setting.web import HTTP_SERVER_DEBUG, WEB_PATH_PRODUCTION, WEB_PATH_DEVELOP
from handler.base import MainHandler, StaticHandler, SigninHandler, SignoutHandler
from handler.app import AppHandler


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', MainHandler),
            (r'/signin', SigninHandler),
            (r'/signout', SignoutHandler),
            (r'/app', AppHandler),
            (r'/(.*)', StaticHandler, {'path': os.path.dirname(__file__)}),
        ]
        settings = {
            'debug': HTTP_SERVER_DEBUG,
            'cookie_secret': COOKIE_SECRET,
            'template_path': os.path.dirname(__file__),
            'static_path': os.path.dirname(__file__),
            'web_path_production': WEB_PATH_PRODUCTION,
            'web_path_develop': WEB_PATH_DEVELOP,
        }
        super(Application, self).__init__(handlers=handlers, **settings)
        self.pool = DBConnectionPool(init_idle_connections=5, **MYSQLCONF)
        self.init_logger()

    @staticmethod
    def init_logger():
        logger = logging.getLogger(name='application')
        # file handler
        fh = logging.FileHandler('application.log')
        fh.setLevel(logging.DEBUG)
        # console handler
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        # log formatter
        fmt = '%(asctime)-15s - %(levelname)s - %(name)s - %(filename)s %(lineno)d - %(message)s'
        datefmt = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(fmt, datefmt)
        # setting log
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)
        logger.addHandler(fh)
        logger.addHandler(sh)
        # 日志信息不向上传递
        logger.propagate = False