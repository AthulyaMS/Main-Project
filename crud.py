from fastapi import Depends,FastAPI,HTTPException,status,UploadFile,BackgroundTasks
from sqlalchemy.orm import Session
import models, schemas,database
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from werkzeug.security import check_password_hash, generate_password_hash
from jose import JWTError,jwt
import datetime
from datetime import  timedelta
import database
from typing import Union
import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM ="HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


####GET USERS
def get_users(db: Session):
   return db.query(models.User).all()


##GET USER BY NAME
def get_user_by_username(db: Session, username: str):
   return db.query(models.User).filter(models.User.username == username).first()


##VERIFY PASSWORD
def verify_password(plain_password, hashed_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)


##CREATE USER
def create_user(db: Session, user: schemas.UserIn):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_pwd=pwd_context.hash(user.password)
    db_user = models.User(username = user.username, email=user.email,password=hashed_pwd,place=user.place)
    db.add(db_user) # add that instance object to your database session
    db.commit() # commit the changes to the database (so that they are saved).
    db.refresh(db_user) # refresh your instance
    return db_user
   


###AUTHENTICATE USER
def authenticate_user(fake_db, username: str, password: str):
    user = get_user_by_username(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


##Function to generate a new access token
def create_access_token(data: dict, expires_delta ):
   SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
   ALGORITHM = "HS256"
   to_encode = data.copy()
   if expires_delta:
      expire = datetime.datetime.utcnow() + expires_delta
      print(expire)
      to_encode.update({"exp": expire})
   else:
      expire = datetime.datetime.utcnow() + timedelta(minutes=15)
      to_encode.update({"exp": expire})
   encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
   return encoded_jwt


###GET TOKEN
def get_current_user(db: Session, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data=schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user=get_user_by_username(db,username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


####CREATE REVIEW TABLE 
def create_review_table(db:Session,mainpath,username):
    db_user=models.review(url=mainpath,username=username,data='null',status=0)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# def review_table_getid(db:Session,mainpath:str):
#     id_d=db.query(models.review.id).filter(models.review.url==mainpath).first()['id']
#     return id_d

def review_table_getid(db:Session,mainpath:str):
    obj=db.query(models.review).all()
    return obj[-1].id



def update_password(db: Session, username, plainpassword,newpassword):
    update_db_user = db.query(models.User).filter(models.User.username == username).first()
    if update_db_user:
        schemas.UserIn.password_validator(newpassword)
        if verify_password (plainpassword, update_db_user.password):
            update_db=db.query(models.User).filter(models.User.username == username).update({models.User.password:pwd_context.hash(newpassword)},synchronize_session=False)
            db.commit()
            return update_db
        else:
            return False
    else:
        return False

    

def getpath(db:Session,new_id):
    return db.query(models.review).filter(models.review.id==new_id).first()



def delete_user(db:Session ,username):
    del_db_user=db.query(models.User).filter(models.User.username==username).first()
    delete_username=del_db_user.username
    db.delete(del_db_user)
    db.commit()
    return delete_username

def find_user(db:Session,token:str):
    newpayload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    username=newpayload.get("sub")
    return username



def status_check(db:Session,id:uuid):
    stat_user=db.query(models.review).filter(models.review.id==id).first()
    statusvalue=stat_user.status
    return statusvalue



def if_success(db:Session,id:uuid,json_str):
    db.query(models.review).filter(models.review.id==id).update({models.review.data:json_str,models.review.status:1},synchronize_session=False)
    db.commit()
    return "success"




def if_fail(db:Session,id:uuid):
    db.query(models.review).filter(models.review.id==id).update({models.review.status:2},synchronize_session=False)
    db.commit()
    return "Failed"





def validate_token(db: Session, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data=schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user=get_user_by_username(db,username=token_data.username)
    if user is None:
        raise credentials_exception
    return "user"



