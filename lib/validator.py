# coding=utf-8
#
# : 提供两个装饰器，对对象属性或方法参数进行校验
#
# : 类装饰器，检查对象属性
# @checkattr(phone=(NotNone, StrLength(11)))
# @checkattr(email=EmailFormat)
# class TestClass(object):
#     def __init__(self, phone=None, email=None):
#         self.phone = phone
#         self.email = email
#
# : 方法装饰器，检查方法参数
# @checkargs(phone=StrLength(11), email=(NotNone, EmailFormat))
# def test_func(phone, email=None, *args, **kwargs):
#     pass
#
# : 可以继承`CheckRule`类自定义规则
#
# : `CheckError`检测失败时抛出的异常类
#
# : 现有规则:
# NotNone: 为空校验
# StrLength: 字符串长度
# StrRegex: 字符串正则匹配
# EmailFormat: 邮件格式
#
import inspect
import re


class CheckError(Exception):
    def __init__(self, message=''):
        self.message = message

    def __str__(self):
        return self.message


class CheckRule(object):
    def __init__(self):
        pass

    def check(self, key, value):
        raise NotImplementedError()

    def __call__(self, *args, **kwargs):
        return self


class NotNone(CheckRule):
    def __init__(self):
        super(NotNone, self).__init__()

    def check(self, key, value):
        if value is None:
            raise CheckError('<{}> None value.'.format(key))


class StrLength(CheckRule):
    def __init__(self, length):
        self.len = length
        super(StrLength, self).__init__()

    def check(self, key, value):
        if isinstance(value, str):
            if not len(value) == self.len:
                raise CheckError('<{}> Invalid length {},expected {}'.format(key, len(value), self.len))
        else:
            raise CheckError('<{}> Not str type'.format(key))


class StrRegex(CheckRule):
    def __init__(self, pattern):
        self.pattern = pattern
        super(StrRegex, self).__init__()

    def check(self, key, value):
        if not re.match(self.pattern, value):
            raise CheckError("<{}> Invalid str value pattern,expected '{}'".format(key, self.pattern))


class EmailFormat(CheckRule):
    def __init__(self):
        super(EmailFormat, self).__init__()

    def check(self, key, value):
        if not re.match(r'^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$', value):
            raise CheckError('<{}> Invalid email format.'.format(key))


def checkattr(**rules):
    """
    类装饰器，将属性与检测规则类的映射关系注册给类，并重写被装饰类的__setattr__方法，
    在给属性赋值时在映射中查找对应检测类并执行检测工作
    """
    def decorator(cls):
        if not inspect.isclass(cls):
            raise CheckError('Invalid decorated type {}.'.format(type(cls)))
        _rules_mapping = {attr: list(rule) if isinstance(rule, (list, tuple)) else [rule] for attr, rule in rules.items()}
        if hasattr(cls, '_rules'):
            _rules = getattr(cls, '_rules')
            for attr, rule in _rules_mapping.items():
                if attr in _rules:
                    _rules[attr].extend(rule)
                else:
                    _rules[attr] = rule
        else:
            cls._rules = _rules_mapping

        def _setattr(self, key, value):
            if key in self._rules:
                map(lambda rule: rule().check('{}.{}'.format(cls.__name__, key), value), self._rules[key])
            super(cls, self).__setattr__(key, value)
        cls.__setattr__ = _setattr
        return cls
    return decorator


def checkargs(**rules):
    """
    方法装饰器，在执行方法时获取方法调用参数，并遍历检测规则，如果指定规则的参数在调用参数列表中，执行该规则
    注意：该装饰器不能在同一方法上用多次，因为多重装饰情况下无法正确获取目标函数的调用参数
    """
    def decorator(func):
        if not inspect.isfunction(func):
            raise CheckError('Invalid decorated type {}.'.format(type(func)))

        def wrapper(*args, **kwargs):
            callargs = inspect.getcallargs(func, *args, **kwargs)
            callargs.update(kwargs)
            for key, rule in rules.items():
                if key in callargs:
                    if isinstance(rule, (list, tuple)):
                        map(lambda _rule: _rule().check('{}.{}'.format(func.__name__, key), callargs[key]), rule)
                    else:
                        rule().check('{}.{}'.format(func.__name__, key), callargs[key])
            func(*args, **kwargs)
        return wrapper
    return decorator


@checkattr(phone=(NotNone, StrLength(11)))
@checkattr(email=EmailFormat)
class TestClass(object):
    def __init__(self, phone=None, email=None):
        self.phone = phone

        self.email = email


@checkargs(phone=StrLength(11), email=(NotNone, EmailFormat))
def test_func(phone, email=None, *args, **kwargs):
    pass


if __name__ == '__main__':
    t = TestClass(phone='1111111111', email='12345@gmail.com')
    # t.phone = None
    test_func('11111111111', email='12345@', we='we')