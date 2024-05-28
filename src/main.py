from fastapi import FastAPI

from api import user

app = FastAPI()
app.include_router(user.router)

@app.get("/")
def haelth_check_handler():
    return {"Hello": "World"}