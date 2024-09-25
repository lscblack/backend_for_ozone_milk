from pydantic import BaseModel, Field, constr, condecimal
from typing import Optional

# Schema for creating a new product
class ProductCreateSchema(BaseModel):
    product_name: constr(min_length=1, max_length=255)
    product_price: condecimal(decimal_places=2, max_digits=10)  # Example for price validation
    date: Optional[str] = Field(None, description="Date when the product was added")

    class Config:
        orm_mode = True

# Schema for updating an existing product
class ProductUpdateSchema(BaseModel):
    product_name: Optional[constr(min_length=1, max_length=255)]
    product_price: Optional[condecimal(decimal_places=2, max_digits=10)]
    date: Optional[str]

    class Config:
        orm_mode = True

# Schema for returning product information
class ProductResponseSchema(BaseModel):
    pro_id: int
    product_name: str
    product_price: str
    date: str

    class Config:
        orm_mode = True
