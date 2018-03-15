# coding=utf-8
# A simple wsgi web framwork

import os
import sys
import re
import threading
import json
import cgi
import traceback
import base64
import hashlib
import mimetypes
from functools import partial
from Cookie import SimpleCookie
from datetime import *

SESSION_ID = 'fsession'
SESSION_KEY = 'private encrypt key'
LOG_FILE = '/tmp/favoor.log'

HTTP_STATUS_CODES = {
    # Informational
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',

    # Successful
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi Status',
    226: 'IM Used',

    # Redirection
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',

    # Client Error
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    418: "I'm a teapot",
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',

    # Server Error
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    507: 'Insufficient Storage',
    510: 'Not Extended',
}


class HttpException(Exception):
    """http error handler."""
    code = None
    description = None

    def __init__(self, code=None, description=None):
        super(HttpException, self).__init__()
        if code is not None:
            self.code = code
        if description is not None:
            self.description = description

    def __str__(self):
        return '%s' % self.description


class Redirect(HttpException):
    """Raise if want to make a 302 client jump."""
    code = 302
    description = '302 client jump.'

    def __init__(self, location):
        self._location = location

    @property
    def location(self):
        return self._location


class BadRequest(HttpException):
    """Raise if server get a bad request"""
    code = 400
    description = 'Bad request that server can not understand.'


class NotFound(HttpException):
    """Raise if the requested URL was not found on the server."""
    code = 404
    description = 'The requested URL was not found on the server.'


class InternalServerError(HttpException):
    """Raise if the server encountered an internal error"""
    code = 500
    description = 'The server encountered an internal error.'


class Log(object):
    """A simple log"""

    @staticmethod
    def error(msg):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(now + os.linesep + msg + os.linesep)
        except Exception as e:
            pass


class ContextStack(threading.local):
    """hold the context,behave like a stack."""

    def __init__(self):
        self._stack = []

    def push(self, obj):
        return self._stack.append(obj)

    def pop(self):
        return self._stack.pop()

    @property
    def top(self):
        try:
            return self._stack[-1]
        except Exception as e:
            return None


class RequestContext(object):
    """请求上下文，包含了请求对象和会话对象"""

    def __init__(self, environ):
        self.request = Request(environ)
        self.session = Session(self.request.get_cookie(SESSION_ID))


class Request(object):
    """request wrapper class."""

    def __init__(self, environ):
        self._environ = environ
        self._cookies = self.cookie

    @property
    def environ(self):
        return self._environ

    @property
    def path_info(self):
        return self._environ.get('PATH_INFO', '')

    def _load_form_data(self):
        # 第一次请求form时封装，之后就不用再处理
        if '_form' in self.__dict__:
            return

        fs = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ, keep_blank_values=True)
        form = dict()
        for key in fs:
            form[key] = fs[key].value
        d = self.__dict__
        d['_form'] = form

    @property
    def form(self):
        self._load_form_data()
        return self._form

    @property
    def cookie(self):
        cookie = SimpleCookie()
        request_cookie = self._environ.get('HTTP_COOKIE')
        if request_cookie:
            cookie.load(request_cookie)
        return cookie

    def get_cookie(self, name):
        try:
            return self._cookies[name].value
        except KeyError:
            return None


class Session(object):
    """Session wrapper class. session数据将存储在一个带有签名的cookie中。
    cookie中的数据格式：key1=value1,key2=value2.signature。
    session data是一个字典。
    """

    def __init__(self, cookie_encrypted):
        self._modified = False
        if cookie_encrypted is None:
            self._session_data = dict()
        else:
            self._session_data = self.decrypt_session(cookie_encrypted)

    def get(self, key):
        return self._session_data.get(key, None)

    def set(self, key, value):
        self._session_data[key] = str(value)
        self._modified = True

    def clear(self, key):
        self._session_data.pop(key, None)
        self._modified = True

    @property
    def modified(self):
        return self._modified

    def decrypt_session(self, cookie_encrypted):
        result = dict()
        s = base64.urlsafe_b64decode(cookie_encrypted)
        pos = s.find('.')
        if pos > 0:
            session = s.rsplit('.', 1)
            session_data = session[0]
            session_signature = session[1]
            if session_signature == self.signature(session_data):
                for item in session_data.split(','):
                    kv = item.split('=')
                    result[kv[0]] = kv[1]
        return result

    def encrypt_session(self):
        """如果session对象被改变，并且session data是一个空字典，说明要清空session，返回None;
        否则将session data签名并返回。
        """
        if not self._session_data:
            return None
        l = list()
        for k, v in self._session_data.iteritems():
            l.append(k + '=' + v)
        session_str = ','.join(l)
        signature = self.signature(session_str)
        return base64.urlsafe_b64encode(session_str + '.' + signature)

    @staticmethod
    def signature(session_str):
        h = hashlib.sha1()
        h.update(session_str + '.' + SESSION_KEY)
        return h.hexdigest()


class Response(object):
    """Response wrapper class."""
    default_status_code = 200
    default_charset = 'utf-8'
    default_content_type = 'application/json'
    default_server = 'favoor/1.0'

    def __init__(self, response=None, status_code=None, content_type=None):
        self.response = response
        self.status_code = self.default_status_code if status_code is None else status_code
        self.content_type = self.default_content_type if content_type is None else content_type
        self.headers = [('Content-Type', self.content_type + '; charset=' + self.default_charset),
                        ('Server', self.default_server)]

    def add_header(self, key, value):
        self.headers.append((key, value))

    def del_header(self, key):
        new = []
        for k, v in self.headers:
            if k.lower() != key.lower():
                new.append((k, v))
        self.headers[:] = new

    @property
    def get_headers(self):
        return self.headers

    def set_cookie(self, key, value):
        """如果value为None，则认为清除该cookie"""
        cookie = SimpleCookie()
        cookie[key] = value
        cookie[key]['path'] = '/'
        expires = - (3600 * 24) if value is None else 3600 * 24
        cookie[key]['expires'] = (datetime.now() + timedelta(seconds=expires)).strftime('%a, %d %b %Y %H:%M:%S')
        self.headers.append(('Set-Cookie', cookie[key].OutputString()))

    def get_response_data(self):
        if self.content_type == self.default_content_type:
            output = dict(
                code=self.status_code,
                data=None,
                msg=None
            )
            if self.status_code >= 400:
                output['msg'] = self.response
            else:
                output['data'] = self.response
            return json.dumps(output)
        return self.response

    def get_response_status(self):
        try:
            status = '%d %s' % (self.status_code, HTTP_STATUS_CODES[self.status_code])
        except KeyError:
            status = '%d Unknown' % self.status_code
        return status

    def get_response_headers(self):
        return self.headers

    def __call__(self, start_response):
        status = self.get_response_status()
        headers = self.get_response_headers()
        response = self.get_response_data()
        # for dev
        self.add_header('Access-Control-Allow-Origin', '*')
        start_response(status, headers)
        return response


class Proxy(object):
    """一个代理，在调用的时候才获得对象并返回对象属性
    """

    def __init__(self, func):
        self._func = func

    def _get_current_object(self):
        return self._func()

    def __getattr__(self, key):
        return getattr(self._get_current_object(), key)


def _lookup_req_object(name):
    """LocalStack栈的最顶端取出RequestContext对象，该对象包含request和session"""
    top = ctx.top
    return getattr(top, name)


request = Proxy(partial(_lookup_req_object, 'request'))
session = Proxy(partial(_lookup_req_object, 'session'))


class Route(list):
    """a route class."""

    def __init__(self):
        super(Route, self).__init__()

    def route(self, path):
        def decorator(func):
            route_pattern = self.build_route(path)
            self.append((route_pattern, func))
            return func

        return decorator

    @staticmethod
    def build_route(path):
        route_regex = re.sub(r"(<[a-zA-Z_]\w+>)", r"(?P\1\w+)", path)
        return re.compile("^{}$".format(route_regex))


ctx = ContextStack()


class Favoor(object):
    """The favoor object implements a WSGI application."""

    def __init__(self, root_path):
        sys.path.append(root_path)
        self._root_path = root_path
        self._routes = []

    def register_view(self, route):
        """register view modules."""
        if not isinstance(route, Route):
            pass
        else:
            self._routes.extend(route)

    def dispatch_request(self):
        """resolve request path_info."""
        path = ctx.top.request.path_info
        if path.startswith('/static/'):
            return self.dispatch_static_files(path)
        for route_pattern, func in self._routes:
            m = route_pattern.match(path)
            if m:
                return func(**m.groupdict())
        raise NotFound()

    def dispatch_static_files(self, path):
        file_path = os.path.join(self._root_path, path[1:])
        if not os.path.isfile(file_path):
            raise NotFound()
        file_ext = os.path.splitext(file_path)[1]
        content_type = mimetypes.types_map.get(file_ext.lower(), 'application/octet-stream')
        file_content = self._gen_static_file(file_path)
        return Response(file_content, content_type=content_type)

    @staticmethod
    def _gen_static_file(path):
        with open(path, 'rb') as f:
            block = f.read(2048)
            while block:
                yield block
                block = f.read(2048)

    @staticmethod
    def save_session(session, response):
        response.set_cookie(SESSION_ID, session.encrypt_session())

    def make_response(self, rv):
        """convert rv into a response object,if rv is response already,do nothing."""
        if isinstance(rv, Exception):
            if not issubclass(type(rv), HttpException):
                # log all unknown exception
                Log.error(traceback.format_exc())
                rv = InternalServerError()
            response = Response(rv.description, rv.code)
            # 如果捕获到的异常是重定向，添加Location header
            if isinstance(rv, Redirect):
                response.add_header('Location', rv.location)
        else:
            response = rv if isinstance(rv, Response) else Response(rv)
            session = ctx.top.session
            if session.modified:
                self.save_session(session, response)
        return response

    def wsgi_app(self, environ, start_response):
        ctx.push(RequestContext(environ))
        try:
            try:
                rv = self.dispatch_request()
                response = self.make_response(rv)
            except Exception as e:
                response = self.make_response(e)
            return response(start_response)
        finally:
            ctx.pop()

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

    def run(self, host='127.0.0.1', port=8080):
        from wsgiref.simple_server import make_server
        server = make_server(host, port, self.wsgi_app)
        print 'Serving HTTP on ' + host + ':' + str(port) + '...'
        server.serve_forever()
