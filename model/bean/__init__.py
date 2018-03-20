# coding=utf-8
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class BaseModel(Base):
    def __init__(self):
        pass

    def __repr__(self):
        return "{}(id='{}')".format(type(self).__name__, getattr(self, 'id'))