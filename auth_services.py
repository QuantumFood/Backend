from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import model, schema
from utils import config, auth


def register_db_user(user: schema.UserCreate, db: Session):
    hashed_password = config.get_password_hash(user.password)
    new_user = model.User(username=user.username.lower(),
                          email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user



def register_keycloak_user(user: schema.UserCreate):
    keycloak_register_data = {
        "username": user.username.lower(),
        "email": user.email,
        "enabled": True,
        "credentials": [
            {
                "type": "password",
                "value": user.password,
                "temporary": False
            }
        ]
    }
    try:
        is_registered = auth.create_user(keycloak_register_data)
        if is_registered == 201:
            return {"message": "User registered successfully"}
        return is_registered
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error registering user")


def delete_db_user(username, db: Session):
    user = db.query(model.User).filter(model.User.username == username).first()
    if user:
        user_request = db.query(model.Request).filter(model.Request.user_id == user.id).first()
        if user_request:
            db.delete(user_request)
        db.delete(user)
        db.commit()
        return {"message": "User deleted successfully"}