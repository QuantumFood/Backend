from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session
from typing import List,Dict
from database import db
from models import model, schema
from utils import auth

router = APIRouter(
    prefix="/requests",
    tags=["requests"],
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schema.Request])
def get_requests(db: Session = Depends(db.get_db)):
    requests = db.query(model.Request).all()
    return requests


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_request(request: schema.Request, db: Session = Depends(db.get_db)):
    if not auth.user_exists_in_keycloak(request.username):
        raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not auth.is_user_logged_in(request.username):
        raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail="User not logged in")
    if db.query(model.Request).filter(model.Request.username == request.username).first():
        raise HTTPException(
              status_code=status.HTTP_409_CONFLICT, detail="User already has a request")
    new_request = model.Request(username=request.username, food=request.food)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return {"message": "Order successfully created", "data": new_request}

