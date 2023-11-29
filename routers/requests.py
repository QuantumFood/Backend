from fastapi import Depends, APIRouter, HTTPException, status,Header
from sqlalchemy.orm import Session, joinedload
from kafka import KafkaProducer
from database import db
from models import model, schema
from utils import auth
import json


router = APIRouter(
    prefix="/requests",
    tags=["requests"],
)



producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

@router.get("/all", status_code=status.HTTP_200_OK)
def get_requests(db: Session = Depends(db.get_db)):
    requests = db.query(model.Request).options(joinedload(model.Request.user)).all()
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
    
    message = {
        "message": "Request created successfully",
        "data": {
            "food": new_request.food,
            "username": user.username,
            "email": user.email
        }
    }
    producer.send('user-requests', message.get("data"))
    producer.flush()
    #comsume_messages()

    return message
    

@router.get("/", status_code=status.HTTP_200_OK)
async def get_requests_by_user(db: Session = Depends(db.get_db), token: str = Header(...)):
    payload  = auth.verify_token(token)
    if not payload:
        raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")    
    username = payload.get("preferred_username")
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    request = db.query(model.Request).filter(model.Request.user_id == user.id).all()
    return request


@router.put("/", status_code=status.HTTP_200_OK)
async def update_request(request: schema.Request, db: Session = Depends(db.get_db), token: str = Header(...)):
    payload  = auth.verify_token(token)
    if not payload:
        raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")    
    username = payload.get("preferred_username")
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db_request = db.query(model.Request).filter(model.Request.user_id == user.id).first()
    if not db_request:
        raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    db_request.food = request.food
    db.commit()
    db.refresh(db_request)
    return {"message": "Request updated successfully","data":{"food":db_request.food}}


@router.delete("/all", status_code=status.HTTP_200_OK)
def delete_all_requests(db:Session=Depends(db.get_db), token: str = Header(...)):
    payload  = auth.verify_token(token)
    if not payload:
        raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")    
    db.query(model.Request).delete()
    db.commit()
    return {"message": "All requests deleted successfully"}