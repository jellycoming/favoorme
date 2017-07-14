# coding=utf-8
import os
import tornado.web
import tornado.escape
from urllib import quote
from tornado.httpclient import AsyncHTTPClient
from lib.exception import MyException, MissingArgument, InternalServerError
from lib.logger import logger


class Response(dict):
    """
    所有请求统一返回格式
    """
    def __init__(self, code=200, msg='', data=None):
        super(Response, self).__init__()
        self['code'] = code
        self['msg'] = msg
        self['data'] = data


class Basehandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @property
    def db(self):
        return self.application.pool.connection()

    def get_current_user(self):
        return self.get_secure_cookie('user')
    
    def __init__(self, application, request, **kwargs):
        super(Basehandler, self).__init__(application, request, **kwargs)
        if request.method == 'POST':
            try:
                self._post_data = tornado.escape.json_decode(self.get_body_argument('data'))
            except Exception as e:
                self.finish(Response(code=MissingArgument.code, msg=str(e)))
        self.http_client = AsyncHTTPClient()

    def prepare(self):
        if not self.current_user:
            self.redirect('/login?_callback=' + quote(self.request.protocol + '://' + self.request.host + self.request.uri))
        else:
            logger.debug('already signed in.')
            pass

    @property
    def data(self):
        return self._post_data

    def _handle_request_exception(self, e):
        if not isinstance(e, MyException):
            e = InternalServerError(description=str(e))
        self.finish(Response(code=e.code, msg=e.description))

    @staticmethod
    def handle_api_response(response):
        # if not response.code == 200:
        #     raise MyException(description=str(response.error))
        pass


class MainHandler(Basehandler):
    """
    返回主页面
    """
    def get(self):
        if 'debug' in self.request.query_arguments:
            web_path = self.settings.get('web_path_develop')
            self.set_cookie('debug', '', expires_days=None)
        else:
            web_path = self.settings.get('web_path_production')
            self.clear_cookie('debug')
        self.render(web_path + '/index.html')


class StaticHandler(tornado.web.StaticFileHandler):
    """
    处理静态文件
    """
    def initialize(self, path, default_filename=None):
        # if not ('.' in self.request.uri and self.request.uri.rsplit('.', 1)[-1].split('?', 1)[0] in self.settings.get('web_allowed_file_ext')):
        #     raise tornado.web.HTTPError(400)
        path = os.path.join(path, self.web_path)
        super(StaticHandler, self).initialize(path, default_filename)

    @property
    def web_path(self):
        return self.settings.get('web_path_develop') if 'debug' in self.request.query_arguments else self.settings.get('web_path_production')

    def data_received(self, chunk):
        pass


class AuthHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, application, request, **kwargs):
        super(AuthHandler, self).__init__(application, request, **kwargs)
        self._baseurl = self.request.protocol + '://' + self.request.host
        try:
            self._callbackurl = self.get_argument('_callback')
        except Exception:
            self._callbackurl = quote(self._baseurl)


class SigninHandler(AuthHandler):
    def get(self):
        # get user...
        user = 'user'
        if not user:
            self.write('User not found in system.')
        else:
            self.set_secure_cookie('user', user)
            self.set_cookie('m_user', user)
        return self.redirect(self._callbackurl)


class SignoutHandler(AuthHandler):
    def get(self):
        self.clear_cookie('user')
        return self.redirect(self._callbackurl)