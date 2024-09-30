from pydantic import BaseModel, Field, conint, condecimal
from typing import Optional
from datetime import date

class StockCreateSchema(BaseModel):
    product_id: int
    product_quantity: Optional[int]
    price_per_unit: float
    total_price: Optional[float]
    date: Optional[date]

    class Config:
        orm_mode = True

class StockUpdateSchema(BaseModel):
    product_quantity: Optional[conint(ge=0)] = None
    price_per_unit: Optional[float] = None
    total_price: Optional[float] = None
    date: Optional[date]

    class Config:
        orm_mode = True

class StockResponseSchema(BaseModel):
    stock_id: int
    product_id: int
    product_quantity: int
    price_per_unit: str
    total_price: Optional[str]
    date: Optional[date]
    product_name: str  # Included product name
    product_type: str  # Included product type

    class Config:
        orm_mode = True
