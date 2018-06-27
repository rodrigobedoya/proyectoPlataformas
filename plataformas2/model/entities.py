from sqlalchemy import Column, Integer, String,Sequence
from database import connector

class User(connector.Manager.Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    position = Column(String(50))
    username = Column(String(50))
    password = Column(String(12))
    email = Column(String(100))
    question = Column(String(150))
    answer = Column(String(150))

class Show(connector.Manager.Base):
    __tablename__ = 'shows'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    imageurl = Column(String(250))
    description = Column(String(1200))
    seasons = Column(String(3))
    episodes = Column(String(6))
    votes = Column(String(7))
    rating = Column(String(13))
    rank = Column(String(5))

class Vote(connector.Manager.Base):
    __tablename__ = 'votes'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    voterId = Column(String(22))
    showId = Column(String(22))
    rating = Column(String(2))