from pydantic import BaseModel
import re
from pydantic import validator
from typing import Union
import uuid
from uuid import UUID
from sqlalchemy_utils import database_exists
from sqlalchemy_utils import UUIDType
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from database import Base
from sqlalchemy_utils import UUIDType
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid
from fastapi import Depends, FastAPI, HTTPException, status





class UserIn(BaseModel):
    username: str
    email: str
    password: str
    place:str



    @validator('password')
    def password_validator(cls, password):
        errors=[]
        if not re.search('[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter.')
        if not re.search('[a-z]', password):
            errors.append('Password must contain at least one lowercase letter.')
        if not re.search('[0-9]', password):
            errors.append('Password must contain at least one digit.')
        if not re.search('[^\w\s]', password):
            errors.append('Password must contain at least one special character.')
        if errors:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=errors)
        return password
    
    @validator("email")
    def validate_email(cls,value):
        if not re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b',value):
            raise ValueError ("Not valid email")
        return value

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str
    place:str

    class Config:
       orm_mode = True

# class review(BaseModel):
   
#     id:uuid.UUID
#     url:str
#     Content_type:str
#     Rating:int
#     Status:int

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None



    