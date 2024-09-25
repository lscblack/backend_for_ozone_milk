from sqlalchemy import Column, Integer, String,Text, Boolean, Float, Date, ForeignKey,DateTime,ARRAY
from db.database import Base
from datetime import date
from datetime import datetime


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, default="")  # Non-nullable for uniqueness
    password = Column(String(255),  nullable=True, default="")  # Non-nullable for uniqueness

class Products(Base):
    __tablename__ = "products"
    Pro_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), unique=True, nullable=False, default="")  # Non-nullable for uniqueness
    product_price = Column(String(255),  nullable=True, default="")  # Non-nullable for uniqueness
    date = Column(String(255),  nullable=True, default="")  # Non-nullable for uniqueness