from pydantic import BaseModel
from schemas.user import UserSchema

class UserInDB(UserSchema):
    password: str

class LoginResponse(BaseModel):
    status: str
    location: str
    content_type: str
    id: str
    access_token: dict
    token_type: str

class LogOutResponse(BaseModel):
    status: str

class RegisterResponse(BaseModel):
    username: str
    created: str

class DeleteResponse(BaseModel):
    status: str
    message: str
