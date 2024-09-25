from pydantic import BaseModel, EmailStr, validator
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
