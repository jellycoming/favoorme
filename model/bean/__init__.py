# coding=utf-8
from sqlalchemy.ext.declarative import declarative_base


class BaseModel(object):
    def __repr__(self):
        _desc = []
        for k, v in self.__dict__.iteritems():
            if not k == '_sa_instance_state':
                _desc.append("{}='{}'".format(k, v))
        return '{}({})'.format(type(self).__name__, ','.join(_desc))


Base = declarative_base(cls=BaseModel)