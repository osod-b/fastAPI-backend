from pydantic import BaseModel, constr, Field
from validators.users import PasswordValidator, EmailValidator, UsernameValidator, RoleValidator, LogInValidator

class UserSchema(BaseModel):
    username: UsernameValidator
    email: EmailValidator
    password: PasswordValidator
    role: RoleValidator
    date_created: str = Field(frozen=True)
    active: bool = Field(frozen=True, default=True)
    root: bool = Field(frozen=True, default=False)

    class Config:
        from_attributes = True

class UserRegistration(BaseModel):
    username: UsernameValidator
    email: EmailValidator
    password: PasswordValidator
    
    model_config = {
        "from_attributes": True 
    }

class UserLogin(BaseModel):
    identifier: LogInValidator
    password: PasswordValidator
    remember_me: bool = Field(default=False)

class RegisterEntity(BaseModel):
    state: str
    post: UserRegistration
    new_user: UserSchema


class UserDelete(BaseModel):
    ...