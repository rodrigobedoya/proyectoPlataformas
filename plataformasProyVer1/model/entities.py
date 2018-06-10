from sqlalchemy import Column, Integer, String
from database import connector

class User(connector.Manager.Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    position = Column(String(50))
    username = Column(String(50))
    password = Column(String(12))

class Show(connector.Manager.Base):
    __tablename__ = 'shows'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    imageurl = Column(String(200))
    description = Column(String(300))
    rating = Column(String(5))
    rank = Column(String(5))
