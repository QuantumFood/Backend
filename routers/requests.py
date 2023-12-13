from fastapi import Depends, APIRouter, HTTPException, status, Header
from sqlalchemy.orm import Session, joinedload
from database import db
from models import model, schema
from utils import auth
from dotenv import load_dotenv
from datetime import datetime
from utils.config import send_mail


load_dotenv()

router = APIRouter(
    prefix="/requests",
    tags=["requests"],
)



@router.get("/all", status_code=status.HTTP_200_OK)
def get_requests(db: Session = Depends(db.get_db)):
    requests = db.query(model.Request).options(
        joinedload(model.Request.user)).all()
    return requests


@router.post("/food", status_code=status.HTTP_201_CREATED)
async def create_request(request: schema.Request, db: Session = Depends(db.get_db), token: str = Header(...)):
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("preferred_username")
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    food = db.query(model.Request).filter(model.Request.user_id == user.id).order_by(model.Request.created_at.desc()).first()
    
    if food and food.created_at.date() == datetime.now().date():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already has a request for today")

    new_request = model.Request(user_id=user.id, food=request.food)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    send_mail(user.email)
       
    message = {
        "message": "Request created successfully",
        "data": {
            "food": new_request.food,
            "username": user.username,
            "email": user.email
        }
    }
    return message


@router.get("/food", status_code=status.HTTP_200_OK)
async def get_requests_by_user(db: Session = Depends(db.get_db), token: str = Header(...)):
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("preferred_username")
    user = db.query(model.User).filter(model.User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    request = db.query(model.Request).filter(model.Request.user_id == user.id).order_by(model.Request.created_at.desc()).first()
    if request:
        return request
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="You have no request")



@router.delete("/all", status_code=status.HTTP_200_OK)
def delete_all_requests(db: Session = Depends(db.get_db), token: str = Header(...)):
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    db.query(model.Request).delete()
    db.commit()
    return {"message": "All requests deleted successfully"}
