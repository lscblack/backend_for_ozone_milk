from pydantic import BaseModel, EmailStr, validator,Field
from typing import List, Optional, Literal
from datetime import date, datetime
from schemas.returnSchemas import ReturnUser


class CreateUserRequest(BaseModel):  # registeration Schema
    username: str
    password: str


class Token(BaseModel):  # token validation schema
    access_token: str
    token_type: str
    UserInfo: ReturnUser


class FromData(BaseModel):  # token validation schema
    username: str
    password: str


class BalanceCreateSchema(BaseModel):
    balance_type: str  # Should be "opening" or "closing"
    date: Optional[date]
    cash_balance: float
    momo_balance: float

    class Config:
        orm_mode = True

class BalanceResponseSchema(BalanceCreateSchema):
    id: int


class TransactionBase(BaseModel):
    description: str
    amount: float = Field(..., gt=0)
    type: str
    date: date

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(BaseModel):
    description: Optional[str] = None
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[str] = None
    date: Optional[date] = None

class TransactionResponse(TransactionBase):
    id: int

    class Config:
        orm_mode = True