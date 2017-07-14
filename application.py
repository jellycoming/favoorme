# coding=utf-8
import os
import logging
import tornado.web
from lib.mysql import DBConnectionPool
from lib.logger import set_logger_file_handler, set_logger_stream_handler
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
        set_logger_stream_handler(level=logging.DEBUG)
        # set_logger_file_handler(filename='application.log', level=logging.DEBUG)