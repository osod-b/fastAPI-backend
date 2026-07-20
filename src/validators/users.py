from typing import ClassVar

from email_validator import validate_email as val_email, EmailNotValidError, EmailSyntaxError
from pydantic import BaseModel, constr, field_validator

#email min length of email max length of email allow dots but not in row check if endswith @... . com... etc
#min username len max-username len, only latin letters, no special symbols
#allow in password only latin letters ascii, digits, some of special symbols

class UsernameValidator(BaseModel):
    value: constr(min_length=5, max_length=14)

    @field_validator('value')
    def validate_username(cls, v):
        if not v.isalpha():
            raise ValueError("Username can contain only ascii letters")        
        return v

class EmailValidator(BaseModel):
    value: constr(min_length=1, max_length=256)

    @field_validator('value')
    def validate_email(cls, v):
        try:
            val_email(v)
            return v
        
        except (EmailNotValidError, EmailSyntaxError) as e:
            raise ValueError(str(e))
        
class RoleValidator(BaseModel):
    value: constr(min_length=4, max_length=14, pattern='^[a-zA-Z]+$')

    @classmethod
    def check_role(s: str) -> bool:
        return s in ('admin', 'user')

    @field_validator('value')
    def validate_role(cls, v):
        if not cls.check_role(v):
            raise ValueError('Role has inappropriate name')
        return v


#allow in password only latin letters ascii, digits, some of special symbols

class PasswordValidator(BaseModel):
    value: constr(min_length=12, max_length=128, pattern=r'^[a-zA-Z0-9!@#$%^&*()_+=\-\{\}\[\]:;"\'<>,.?/\\|~]+$')

    NUMBERS: ClassVar[int] = 1
    SPECIAL: ClassVar[int] = 1
    UPPERCASE: ClassVar[int] = 1    

    @classmethod
    def spaces_check(cls, s: str) -> bool:
        if ' ' in s:
            return False
        
        return True
        
    @classmethod
    def password_minimal_strength(cls, s: str):
        constraints = {
            'NUMBERS': 0,
            'SPECIAL': 0,
            'UPPERCASE': 0
        }

        for symbol in s:
            if symbol.isupper():
                constraints['UPPERCASE'] += 1
            if symbol.isdigit():
                constraints['NUMBERS'] += 1
            if not symbol.isalnum():
                constraints['SPECIAL'] += 1
        
        return (constraints['NUMBERS'] >= PasswordValidator.NUMBERS and
                constraints['SPECIAL'] >= PasswordValidator.SPECIAL and 
                constraints['UPPERCASE'] >= PasswordValidator.UPPERCASE)


    @field_validator('value')
    def validate_password(cls, v):
        if not cls.spaces_check(v): 
            raise ValueError("Password can't contain whitespaces")
        
        if not cls.password_minimal_strength(v):
            raise ValueError("Password doesn't treshhold minimal strength")

        return v
        

class LogInValidator(BaseModel):
    value: constr(min_length=3, max_length=128)

    @field_validator('value')
    def detect_value_type(cls, v):
        try:
            val = EmailValidator(value=v)
        except Exception:
            pass
        else:
            return val.value
        try:
            val = UsernameValidator(value=v)
        except Exception:
            pass
        else:
            return val.value
        
        raise ValueError("Value must be a valid email or username")
    

class VerificationalCode(BaseModel):
    value: constr(min_length=5, max_length=10, pattern=r'^[a-zA-Z0-9_\-]+$')
