from flask import Flask,render_template,redirect,url_for,jsonify
from database import SessionLocal,engine
import crud,models,schemas
import requests
from flask import Flask,request,flash
from flask_wtf import FlaskForm,file
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms import StringField, PasswordField, SubmitField
from sqlalchemy.dialects.postgresql import UUID
from flask_sqlalchemy import SQLAlchemy
import uuid
import json
from flask import render_template
from sqlalchemy import MetaData, Table
from sqlalchemy.orm import sessionmaker
import pandas as pd
import pandas as pd
from io import StringIO
from flask import Flask, make_response
from sqlalchemy import create_engine
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y-%m-%d %H:%M:%S',
                    filename='users&text_logging.log',filemode='w')




app=Flask(__name__)
app.secret_key = "mysecretkey"
session=SessionLocal()

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
   db.close()

@app.route('/')
def index():
   return render_template('index.html')





class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    place= StringField('place')
    submit = SubmitField('Submit')





@app.route('/signup', methods=['GET', 'POST'])
def signup():
   form = SignupForm()
   if request.method == 'POST':
      username = form.username.data
      email = form.email.data
      password = form.password.data
      place = form.place.data
      url = "http://localhost:8000/create/user/"
         
      data_1={
               "username": username,
               "email": email,
               'password': password,
               'place': place              
               }
      response = requests.post(url, json=data_1)
      logger.debug("Flask Signup response:%s",response.status_code)
      if response.status_code==200:
         flash("signed up!!")
         return render_template('index.html')
      elif response.status_code==401:
         flash(response.json()['detail'])
      else:
         if response.status_code==422:
            try:
               flash(response.json()['detail'][0]['msg'])
            except:
               flash(response.json()['detail'])

   return render_template('signup.html', form=form)


# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#    form = SignupForm()
#    if form.validate_on_submit():
#       username = request.form['username']
#       email = request.form['email']
#       password = request.form['password']
#       place = request.form['place']
#       url = "http://localhost:8000/create/user/"
         
#       payload={
#                "username": username,
#                "email": email,
#                'password': password,
#                'place': place              
#                }
#       requests.post(url, json=payload)
#       flash("successful") 
#       return render_template('signup.html', form=form)
#    else:
#       return render_template('signup.html', form=form)





@app.route('/signin', methods=['GET', 'POST'])
def signin():
   form = SignupForm()
   
   if request.method == 'POST':
         username = form.username.data
         password = form.password.data
         url = "http://localhost:8000/get/token/"
         data={
                  "username": username,
                  'password': password,
                           
                  }
         response = requests.post(url, data=data)
         if response.status_code==200:
            access_token=response.json()['access_token']
            print("signin",access_token)
            return render_template('edit_profile.html',username=username,access_token=access_token)
         else:
            flash('invalid password or username')
   return render_template('signin.html', form=form)



@app.route('/updatepassword',methods=['GET','POST'])
def updatepassword():
   if request.method=='POST':
      username=request.form['username']
      password=request.form['password']
      newpassword=request.form['newpassword']
      url="http://localhost:8000/updatepassword/"
   
      data={
         'username':username,
         'password':password,
         'newpassword':newpassword}
      response=requests.post(url,params=data)
      if response.status_code ==200:
        flash('password updated')
      else:
        flash('failed')
   return render_template("update_password.html") 





@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        username = request.form['username']
        url = "http://localhost:8000/delete"
        response = requests.delete(url,params={'username':username})
        users = session.query(models.User).all()
        return render_template('index.html',users=users)





   


@app.route('/uploadfile', methods=['POST','GET'])
def upload_file():
    if request.method == 'POST':
      token = request.form.get('token')
      print("upload",token)
      file = request.files['file']
      url = 'http://localhost:8000/uploadfile/'
      payload = {'file': file.read()}
      params={'token':token}
      response = requests.post(url, files=payload,params=params)
      print("####",type(response))
      id_d = response.json()['ID']
      print (id_d)
     
      return redirect(url_for('detect_status',token=token,id_d=id_d))
    else:
       token=request.args.get('access_token')
       print(token)
       return render_template("upload.html",token=token )



class Statusform(FlaskForm):
    id_d = StringField('id_d', validators=[DataRequired()])
    token = StringField('token', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


@app.route('/detect_status', methods=['POST','GET'])
def detect_status():
   token=request.args.get('token')
   id_d = request.args.get('id_d')
   url = 'http://localhost:8000/detect_status'
   params = {'id_d':id_d,'token': token}
   response = requests.get(url, params=params)
  
   status=response.json()['status'] 
   print(status)
   useritem=session.query(models.review).filter(models.review.id==id_d).first()
   session.close
   if status=="success":
     db_table=pd.read_json(useritem.data,orient='records')
     dbdict = db_table.to_dict('records')
    
     return render_template('display.html',status=status,dbdict=dbdict,id_d=id_d)
   elif status== "progressing":
      return '<h1>Sentiment analysis is Progressing...</h1>'
   elif status == 'failed':
      return '<h1> Sentiment Analysis is Failed </h1>'
   
   


@app.route('/download')
def download():
    id_d = request.args.get('id_d')
    useritem = session.query(models.review).filter_by(id=id_d).first() 
   #  useritem=session.query(models.review).filter(models.review.id==id_d).first()
    session.close()
    if useritem is not None:
        db_table = pd.read_json(useritem.data, orient='records')
        csvdata = db_table.to_csv(index=False)
        response = make_response(csvdata)
        response.headers['Content-Disposition'] = 'attachment; filename=Predicted_Review.csv' 
        response.headers['Content-Type'] = 'text/csv'
        return response
    else:
        return "No data found for the provided ID"


if __name__=='__main__':
   app.run(debug=True)