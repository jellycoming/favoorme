# coding=utf-8


class MyException(Exception):
    code = None
    description = None

    def __init__(self, code=None, description=None):
        super(MyException, self).__init__()
        if code is not None:
            self.code = code
        if description is not None:
            self.description = description

    def __str__(self):
        return '{}'.format(self.description)


class MissingArgument(MyException):
    code = 400
    
    def __init__(self, arg_name):
        super(MissingArgument, self).__init__()
        self.arg_name = arg_name

    @property
    def description(self):
        return 'Missing argument {}'.format(self.arg_name)


class BadRequest(MyException):
    code = 400
    description = 'Bad request that server can not understand.'


class Forbidden(MyException):
    code = 403
    description = 'Permission denied.'


class NotFound(MyException):
    code = 404
    description = 'The requested URL was not found on the server.'


class InternalServerError(MyException):
    code = 500
    description = 'The server encountered an internal error.'