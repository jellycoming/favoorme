# coding=utf-8
from sqlalchemy import Column, Integer, String
from model.bean import Base


class App(Base):
    __tablename__ = 'entity_app'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    ctime = Column('ctime', String)

    def __init__(self):
        pass

    def __repr__(self):
        return "{}(id='{}',name='{}')".format(type(self).__name__, self.id, self.name)