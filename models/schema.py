from pydantic import BaseModel,EmailStr


class Request(BaseModel):
    food: str


class UserLogin(BaseModel):
    email: str
    password: str
    
class User(BaseModel):
    username: str
    email: EmailStr
    
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str