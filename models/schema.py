from pydantic import BaseModel,EmailStr


class Request(BaseModel):
    username: str
    food: str


class UserLogin(BaseModel):
    username: str
    password: str
    
class User(BaseModel):
    username: str
    email: EmailStr
    
    
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str
    lastName: str
    firstName: str