from pydantic import BaseModel, Field, constr, condecimal
from typing import Optional

# Schema for creating a new product
class ProductCreateSchema(BaseModel):
    product_name: Optional[str] = None
    product_type:  Optional[str] = None
    product_price: Optional[str] = None  # Example for price validation
    date: Optional[str] = None

    class Config:
        orm_mode = True

# Schema for updating an existing product
class ProductUpdateSchema(BaseModel):
    product_name: Optional[str] = None
    product_type:  Optional[str] = None
    product_price: Optional[str] = None
    date:  Optional[str] = None

    class Config:
        orm_mode = True

# Schema for returning product information
class ProductResponseSchema(BaseModel):
    Pro_id: Optional[int] =None
    product_name:  Optional[str] = None
    product_type:  Optional[str] = None
    product_price:  Optional[str] = None
    date:  Optional[str] = None

    class Config:
        orm_mode = True
