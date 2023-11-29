from fastapi import APIRouter, Depends, status, HTTPException, Header
from sqlalchemy.orm import Session
from models import schema,model
from database import db
from utils import auth
from auth_services import delete_db_user, register_db_user, register_keycloak_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: schema.UserCreate, db: Session = Depends(db.get_db)):
    if auth.user_exists_in_keycloak(user.username,user.email):
        raise HTTPException(status_code=409, detail="User already exists")
    try:
        register_keycloak_user(user)
        register_db_user(user, db)
        #login user
        token = auth.get_user_token(user.email,user.password)
        return token
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error registering user,retry later")


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(user: schema.UserLogin):
    token = auth.get_user_token(user.email, user.password)
    return token



@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(token: str = Header(...)):
    response = auth.logout_user(token)
    return response



@router.delete("/users", status_code=status.HTTP_200_OK)
async def delete_user(token: str = Header(...), db: Session = Depends(db.get_db)):
    payload = auth.verify_token(token)
    if not payload:
        raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")    
    username = payload.get("preferred_username")
    auth.delete_keycloak_user(username)
    delete_db_user(username, db)
    return {"message": "User deleted successfully"}


@router.delete("/users/all",status_code=status.HTTP_200_OK)
async def delete_all_users(db: Session = Depends(db.get_db)):
    users = db.query(model.User).all()
    for user in users:
        auth.delete_keycloak_user(user.username)
        delete_db_user(user.username, db)
    return {"message": "All users deleted successfully"}
    
