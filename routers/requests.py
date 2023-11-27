from fastapi import Depends, APIRouter, HTTPException, status,Header
from sqlalchemy.orm import Session
from typing import List
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
async def create_request(request: schema.Request, db: Session = Depends(db.get_db), token: str = Header(...)):
    payload  = auth.verify_token(token)
    if not payload:
        raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")    
    username = payload.get("preferred_username")
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if db.query(model.Request).filter(model.Request.user_id == user.id).first():
        raise HTTPException(
              status_code=status.HTTP_409_CONFLICT, detail="User already has a request")
    
    new_request = model.Request(user_id=user.id, food=request.food)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return {"message": "Request created successfully","data":{"food":new_request.food}}


