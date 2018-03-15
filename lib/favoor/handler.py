# coding=utf-8
# http request hanlder

import re
import time
import hashlib
from functools import wraps
from web import Route, request, Response, session, BadRequest, Redirect, InternalServerError

view = Route()


@view.route('/signup')
def signup():
    args = build_args(request.form, 'email', 'passwd')
    if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', args.get("email")):
        raise BadRequest(description='Invalid email format!')
    args['ctime'] = ctime()
    args['passwd'] = md5(args.get('passwd'))
    # save


@view.route('/login')
def login():
    # args = build_args(request.form, 'email', 'passwd')
    user = {'email': 'public@fuuu.me'}  # get user from db
    session.set('user', user['email'])
    # if user and user['passwd'] == md5(args.get('passwd')):
    #     session.set('user', user['email'])
    # else:
    #     raise BadRequest(description='Invalid email or passwd!')


@view.route('/logout')
def logout():
    session.clear('user')


@view.route('/user')
def current_user():
    user = session.get('user')
    if not user:
        return dict(logged=False)
    return dict(logged=True, user=user)


@view.route("/hi/<name>")
def test(name):
    name += request.path_info
    u = session.get('user')
    login = session.get('login')
    # if not session.get('user'):
    #     raise Redirect('http://www.localhost')
    # raise Redirect('/hi/go/baby')
    res = Response("test on session user %s,logined:%s" % (u, login))
    # res.set_cookie('hello', 'hahaha')
    # res.add_header('Content-Type', 'text/plain')

    # print request.cookie
    # print request.environ
    # print request.form.get('a')
    # print request.get_cookie('helloo')
    session.set('user', 'aka')
    session.set('login', True)

    return res


def login_required(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        if not session.get('user'):
            raise Redirect('http://localhost')
        return func(*args, **kwargs)

    return decorator


def build_args(args, *keys):
    """check and build args"""
    description = None
    if not all(k in args for k in keys):
        description = 'missing parameters!'
    elif not all(args.get(k).strip() for k in keys):
        description = "parameters can't be space!"
    if description:
        raise BadRequest(description=description)
    return {k: args.get(k).strip() for k in keys}


def ctime():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def md5(s):
    h = hashlib.md5()
    h.update(s)
    return h.hexdigest()
