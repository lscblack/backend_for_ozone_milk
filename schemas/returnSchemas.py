from pydantic import BaseModel, EmailStr,validator
from typing import List, Optional, Literal
from datetime import date,datetime


class ReturnUser(BaseModel):
    username: Optional[str] = None
    class Config:
        orm_mode = True
        from_attributes = True  # Enable this to use from_orm