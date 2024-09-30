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
    product_type = Column(String(255), nullable=False, default="")  # Non-nullable for uniqueness
    product_price = Column(String(255),  nullable=True, default="")  # Non-nullable for uniqueness
    date = Column(String(255),  nullable=True, default="")  # Non-nullable for uniqueness
    
class Stock(Base):
    __tablename__ = "stock"
    stock_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.Pro_id"), index=True)  # Corrected foreign key reference
    product_quantity = Column(Integer, nullable=False)  # Quantity should be an integer, not a string
    price_per_unit = Column(String(255), nullable=False)  
    total_price = Column(String(255), nullable=True)  # Changed field name to lowercase
    date = Column(Date, nullable=True)
    
class StockHistory(Base):
    __tablename__ = "StockHistory"
    stock_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.Pro_id"), index=True)  # Corrected foreign key reference
    product_quantity = Column(Integer, nullable=False)  # Quantity should be an integer, not a string
    price_per_unit = Column(String(255), nullable=False)  
    total_price = Column(String(255), nullable=True)  # Changed field name to lowercase
    stocktype = Column(String(255), nullable=True)   
    date = Column(DateTime, default=datetime.utcnow, index=True)
    
class StockOut(Base):
    __tablename__ = "stockOut"
    stock_id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.Pro_id"), index=True)  # Corrected foreign key reference
    product_quantity = Column(Integer, nullable=False)  # Quantity should be an integer, not a string
    price_per_unit = Column(String(255), nullable=False)  
    total_price = Column(String(255), nullable=True)  # Changed field name to lowercase
    date = Column(Date, nullable=True)