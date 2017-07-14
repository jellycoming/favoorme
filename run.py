# coding=utf-8
import tornado.httpserver
import tornado.ioloop
from application import Application

if __name__ == '__main__':
    server = tornado.httpserver.HTTPServer(Application())
    # single instance
    server.listen(8001)
    # multiple instance
    # server.bind(8888)
    # server.start(4)
    tornado.ioloop.IOLoop.instance().start()