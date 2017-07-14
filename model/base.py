# coding=utf-8
from lib.exception import MissingArgument


class BaseModel(dict):
    def __init__(self, **kwargs):
        super(BaseModel, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise MissingArgument(key)

    def __setattr__(self, key, value):
        self[key] = value