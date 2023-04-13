from fastapi import Depends, FastAPI,HTTPException,status,Response
from typing import List
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from datetime import  timedelta
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi import APIRouter
import logging

router=APIRouter()
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
models.Base.metadata.create_all(bind=engine)
app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S',
                    filename='users&text_logging.log',filemode='w')

# Dependency
def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()

try:
   models.Base.metadata.create_all(bind=engine)
except Exception as e:
   logging.critical('Failed in database connection ')



@router.post("/create/user/", response_model=schemas.User)
def create_user(user: schemas.UserIn, db: Session =Depends(get_db)):
  db_user = crud.get_user_by_username(db, username=user.username)
  if db_user:
    logger.warning("Username exists")
    raise HTTPException(status_code=422, detail="username already exists")
  if not schemas.UserIn.password_validator(user.password):
    logger.warning("password error")
    # raise HTTPException(status_code=401,
    #                      detail="password must contain at least one lowercase letter, uppercase letter, digit, and special character")
    # raise HTTPException(status_code=422,
    #                      detail=[
    #       "Password must contain at least one uppercase letter.",
    #       "Password must contain at least one digit.",
    #       "Password must contain at least one special character."
  # ])
  if not schemas.UserIn.validate_email(user.email):
    logger.warning("email error")
    raise HTTPException(status_code=422,detail="error_detail")
  return crud.create_user(db=db, user=user)


# @router.post("/create/user/", response_model=schemas.User,tags=['CREATE USERS'])
# def create_user(user: schemas.UserIn, db: Session =Depends(get_db)):
#     db_user = crud.get_user_by_username(db, username=user.username)
#     if db_user:
#       raise HTTPException(status_code=400, detail="usename already registered")
#     return crud.create_user(db=db, user=user)


   
    



@router.get("/get/users/", response_model=List[schemas.User],tags=['GET USERS'])
def read_users(db: Session = Depends(get_db)):
  users = crud.get_users(db)
  return users 





@router.post("/get/token",tags=['GET TOKEN'])
async def login_for_access_token(db:Session=Depends(get_db),form_data: OAuth2PasswordRequestForm = Depends()):
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    user = crud.authenticate_user(db,form_data.username, form_data.password)
    if not user:
      logger.error("Incorrect username or password")
      raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crud.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}






@router.post("/updatepassword", response_model=List[schemas.User], tags=['UPDATE PASSWORD'])
def update(username: str, password: str, newpassword: str ,db: Session = Depends(get_db)):
    update_user = crud.update_password(db, username, password, newpassword)
    if update_user:
       logger.info("Password updated ")
       return Response(content=f"password of {update_user} has been updated",headers={"Content-Type":"text/html"},status_code=200)
    else:
       logger.error("username/password is incorrect")
       return Response(content=f"incorrect usename or password",headers={"Content-Type":"text/html"},status_code=401)
    





@router.delete("/delete",response_model=List[schemas.User],tags=['Delete user'])
def delete(username:str,db:Session=Depends(get_db)):   
  deleteuser=crud.delete_user(db,username)
  logger.info("User deleted")
  return Response(content=f"User {deleteuser} has been deleted",headers={"Content-Type":"text/html"},status_code=200)


# @router.delete("/deleteuser/")
# async def delete_user(username: str,db: Session = Depends(get_db)):
#   user = db.query(models.User).filter(models.User.username == username).first()
#   if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#   db.delete(user)
#   db.commit()
#   logging.info('User Deleted')
#   return {"message": "User deleted successfully"}   







