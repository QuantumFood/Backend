from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from models import schema
from database import db
from utils import auth
from auth_services import register_db_user, register_keycloak_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# register a new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: schema.UserCreate, db: Session = Depends(db.get_db)):
    if auth.user_exists_in_keycloak(user.username):
        raise HTTPException(status_code=409, detail="User already exists")
    keycloack_user = register_keycloak_user(user)
    register_db_user(user, db)
    return keycloack_user


# user login
@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user: schema.UserLogin):
    token = auth.get_user_token(user.username, user.password)
    return token
