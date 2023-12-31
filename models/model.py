from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean
from sqlalchemy.orm import relationship
import sqlalchemy
from database import db

Base = db.Base

class Request(Base):
    __tablename__ = "requests"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
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
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, server_default=sqlalchemy.func.now(), nullable=False)
    requests = relationship("Request", back_populates="user")