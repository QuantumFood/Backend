from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import db
from models import model
from routers import users, requests


model.Base.metadata.create_all(bind=db.engine)
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router, prefix="/api/v1")
app.include_router(requests.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "WELCOME TO QUANTUM FOOD"}
