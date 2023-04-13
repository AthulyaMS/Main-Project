

from fastapi import FastAPI

from users  import router as alluser
from text import router as textclass


app = FastAPI()

app.include_router(alluser)
app.include_router(textclass)
