# coding=utf-8
from sqlalchemy import Column, Integer, String
from model.bean import BaseModel


class App(BaseModel):
    __tablename__ = 'entity_app'

    id = Column('id', Integer, primary_key=True, autoincrement=True)
    name = Column('name', String)
    ctime = Column('ctime', String)