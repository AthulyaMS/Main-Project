FROM python:3.10
WORKDIR /myvenv
# COPY ./requirements.txt /myvenv/
COPY ./requirements.txt  /myvenv/requirements.txt
# RUN pip install --upgrade pip && pip install -r ./requirements.txt
RUN pip install --upgrade -r /myvenv/requirements.txt
COPY ./myvenv/* /myvenv/
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# FROM python:3.10
# WORKDIR /myvenv
# COPY ./requirements.txt /myvenv/
# RUN pip install --upgrade pip && pip install -r ./requirements.txt
# COPY ./myvenv /myvenv/
# EXPOSE 8000
# EXPOSE 5000
# CMD [ "sh" ,"-c" ,"gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app -b 0.0.0.0.8000 & python flaskcode1.py --port 5000"]
# # CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# FROM python:3.10

# WORKDIR /myvenv

# COPY ./requirements.txt /myvenv/


# RUN pip install --upgrade pip && pip install -r ./requirements.txt

# COPY ./myvenv/* /myvenv/

# EXPOSE 8000

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]