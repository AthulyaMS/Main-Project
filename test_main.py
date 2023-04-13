from crud import *
from fastapi import FastAPI
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import Session
from database import SessionLocal
# import hypothesis
import pytest

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# client = TestClient(app)





@pytest.fixture
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()


# @pytest.fixture
# def client():
#     return TestClient(app)


def test_create_user_username_already_exists(get_db):
    
    assert get_user_by_username(get_db, username='Saly')
  
  


def test_validate_token(get_db):
    
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM = "HS256"
    # generate a valid access token
    valid_token = create_access_token(data={"sub":'Saly'}, expires_delta=access_token_expires)
    # ensure that the token is validated successfully
    assert validate_token(get_db, valid_token) == "user"


def test_validate_invalid_tocken(get_db):
    invalid_token = '1234567890'
    with pytest.raises(HTTPException) as val:
        validate_token ( get_db,invalid_token)
    assert val.value.detail == 'Could not validate credentials'