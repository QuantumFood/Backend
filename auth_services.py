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
    return {"message": "User created successfully", "data": {"username": new_user.username, "email": new_user.email}}


def register_keycloak_user(user: schema.UserCreate):
    keycloak_register_data = {
        "username": user.username,
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
            return {"message": "User registered successfully", "data": {"username": user.username, "email": user.email}}
        return is_registered
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error registering user")
