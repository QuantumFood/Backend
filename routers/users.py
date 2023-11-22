from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from models import model, schema
from database import db
from utils import config, auth

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


# register a new user
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: schema.UserCreate, db: Session = Depends(db.get_db)):
    hashed_password = config.get_password_hash(user.password)
    try:
        new_user = model.User(username=user.username,
                              email=user.email, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        raise HTTPException(status_code=409, detail="User already exists")
    # register on keycloak
    keycloak_register_data = {
        "username": user.username,
        "email": user.email,
        "enabled": True,
        "firstName": user.firstName,
        "lastName": user.lastName,
        "credentials": [
            {
                "type": "password",
                "value": user.password,
                "temporary": False
            }
        ]}
    try:
        is_registered = auth.create_user(keycloak_register_data)
        if is_registered == 201:
            return {"message": "User registered successfully","data":new_user}
        else:
            return is_registered
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error registering user")


# user login
@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(user: schema.UserLogin):
    token = auth.get_user_token(user.username, user.password)
    return token
