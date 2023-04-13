from fastapi import Depends, FastAPI,HTTPException,UploadFile,status,BackgroundTasks,File,Response
from typing import List,Union
from sqlalchemy.orm import Session
import crud, models, schemas
from database import SessionLocal, engine
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
import shutil
import pandas as pd 
import numpy as np 
from fastapi import APIRouter
from transformers import pipeline
import logging
import uuid 
import database
from database import engine
import os


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S',
                    filename='users&text_logging.log',filemode='w')
router=APIRouter()

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()



@router.get("/detect_status",tags=['STATUS DETECTION'])
async def detect_status(token:str,id_d:uuid.UUID,db:Session=Depends(get_db)):
   crud.validate_token(db,token)
   s_value=crud.status_check(db,id_d)
   if s_value==1:
     sval="success"
   elif s_value==0:
      sval="progressing"
   else:
      sval="failed"
   return {"status":sval}


def sentimental_analysis(id_d:uuid,db:Session):
      print("sentimental analysis is started")
      db_csv=crud.getpath(db,id_d).url
      df = pd.read_csv(db_csv)
      # df = df[df['Rating'] != 3]
      # df['Positive_rating'] = np.where(df['Rating'] > 3, 1, 0)                
      
      reviews=list(df['Reviews'])
      classifier=pipeline('sentiment-analysis',model="distilbert-base-uncased-finetuned-sst-2-english")
      max_length=512
      try:
         
         reviews=[review[:max_length] for review in df['Reviews']]
         senti_analysis=classifier(reviews)
         labels=[i['label'] for i in list(senti_analysis)]
         # print(labels)
         df['sentimental_analysis'] =labels
         select_columns = df[['Product Name','Reviews','sentimental_analysis']]
         json_str = select_columns.to_json()
         # db.query(models.review).filter(models.review.id == id_d).update({'data':json_str,'status': 1})
         
         # df.to_sql ('analysis_table',database.engine, if_exists='replace', index=False)
         crud.if_success(db,id_d,json_str)
         print('sentimental_analysis is successfull')
      except Exception as e:
         logger.debug("Error",e)
         crud.if_fail(db,id_d)
         print("sentimental_analysis is failed:",e) 





# file_path="C:/Users/91999/Desktop/sqlalchemy/"
file_path= os.getcwd().replace("\\", "/") + '/'

@router.post("/uploadfile",tags=['Upload Csv File'])
async def create_upload_file(token: str,background_tasks:BackgroundTasks,db:Session = Depends(get_db),file: UploadFile=File(...) ):
    crud.get_current_user(db,token)
    
    with open(f"{file.filename}","wb") as  buffer:
       shutil.copyfileobj(file.file,buffer)
    file_name=file.filename
   #  file_type=file.content_type
    mainpath=file_path+file_name
    username=crud.find_user(db,token)
    if not file:
       logger.error("No file")
       return "No file sent",400
    else:  
       crud.create_review_table(db,mainpath,username)
       id_d=crud.review_table_getid(db,mainpath)
    # message=crud.getpath(db,id_d).url
    background_tasks.add_task(sentimental_analysis,id_d,db)
    return {'ID':id_d}

# docker exec -it 036fcf9d9da6ce5caea9ba5d50c6d50efd916acfdd84c924b8d5ccf0b84a511e bash 