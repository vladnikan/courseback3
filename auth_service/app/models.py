from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from auth_service.app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)