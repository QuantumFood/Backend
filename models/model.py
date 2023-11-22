from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import sqlalchemy
from database import db

Base = db.Base

class Request(Base):
    __tablename__ = "requests"

    email = Column(String, ForeignKey('users.email'), primary_key=True)
    food = Column(String)
    created_at = Column(
        DateTime, server_default=sqlalchemy.func.now(), nullable=False)
    user = relationship("User", back_populates="requests")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(
        DateTime, server_default=sqlalchemy.func.now(), nullable=False)
    requests = relationship("Request", back_populates="user")