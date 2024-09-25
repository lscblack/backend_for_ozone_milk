from pydantic import BaseModel, Field, conint, condecimal
from typing import Optional

class StockCreateSchema(BaseModel):
    product_id: int
    product_quantity: conint(ge=0)
    price_per_unit: condecimal(decimal_places=2, max_digits=10)
    total_price: Optional[condecimal(decimal_places=2, max_digits=10)]
    date: Optional[str] = Field(None, description="Date when the stock was added")

    class Config:
        orm_mode = True

class StockUpdateSchema(BaseModel):
    product_quantity: Optional[conint(ge=0)]
    price_per_unit: Optional[condecimal(decimal_places=2, max_digits=10)]
    total_price: Optional[condecimal(decimal_places=2, max_digits=10)]
    date: Optional[str]

    class Config:
        orm_mode = True

class StockResponseSchema(BaseModel):
    stock_id: int
    product_id: int
    product_quantity: int
    price_per_unit: str
    total_price: Optional[str]
    date: Optional[str]
    product_name: str  # Included product name
    product_type: str  # Included product type

    class Config:
        orm_mode = True
