from fastapi import Depends, APIRouter, status
from sqlalchemy.orm import Session
from typing import List
from database import db
from models import model, schema

router = APIRouter(
    prefix="/requests",
    tags=["requests"],
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.Request])
def get_requests(db: Session = Depends(db.get_db)):
    requests = db.query(model.Request).all()
    return requests


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.Request)
def create_request(request: schema.Request, db: Session = Depends(db.get_db)):
    new_request = model.Request(email=request.email, food=request.food)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return new_request
