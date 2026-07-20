from typing import ClassVar

from email_validator import validate_email as val_email, EmailNotValidError, EmailSyntaxError
from pydantic import BaseModel, field_validator, constr
from uuid import UUID
from fastapi import UploadFile

# 35 - letter's length for each name in format as FirstName and SurName
#add full_name, email, number, verification


class FileType(BaseModel):
    value: str

    @field_validator('value')
    @classmethod
    def validate(cls, v):
        allowed_ft = { 'db', 'xlsx', 'xls', 'csv'}

        if v not in allowed_ft:
            raise ValueError('File type not supported')
        
        return v

class FileVal(BaseModel):
    value: UploadFile

    
    @field_validator('value')
    @classmethod
    def validate_file(cls, v: UploadFile) -> UploadFile:
        allowed_ft = {  'db', 'xlsx', 'xls', 'csv'}

        file_name = v.filename
        if not file_name or '.' not in file_name:
            raise ValueError('File must have a valid extension')
        
        file_type = file_name.rsplit('.', 1)[-1].lower()

        if file_type not in allowed_ft:
            raise TypeError('Not allowed file type')

        return v

class UUIDVal(BaseModel):
    value: str

    @field_validator('value')
    def validate_uuid(cls, v):
        try:
            uuid = UUID(v)
        except (ValueError) as e:
            raise e
        return uuid

class MessageValidator(BaseModel):
    value: constr(min_length=1, max_length=128, pattern="^[a-zA-Z0-9@,.;:#$%&*()+=/') -]*$")

    @field_validator('value')
    def validate_message(cls, v):
        return v

class NameValidator(BaseModel):
    value: constr(min_length=3, max_length=71, pattern='^[a-zA-Z ]+$')

    NAME_LENGTH: ClassVar = 35
    
    @classmethod
    def spaces_check(cls, s: str) -> bool:
        if s.count(' ') != 1:
            return False
        if s.startswith(' ') or s.endswith(' '):
            return False
        return True
    
    @classmethod
    def length_check(cls, s: str) -> str:
        name, surname = s.split(' ')
        if len(name) > cls.NAME_LENGTH or len(surname) > cls.NAME_LENGTH:
            raise ValueError('Name length limit has been exceeded')
        
        return f'{name.capitalize()} {surname.capitalize()}'


    @field_validator('value')
    def validate_name(cls, v):
        if not cls.spaces_check(v):
            raise ValueError('Name must contain exactly one space among credentials')
        capitalized_name = cls.length_check(v)
        
        return capitalized_name

class EmailValidator(BaseModel):
    value: constr(min_length=1, max_length=256)

    @field_validator('value')
    def validate_email(cls, v):
        try:
            val_email(v)
            return v
        except (EmailNotValidError, EmailSyntaxError) as e:
            raise ValueError(str(e))

class PhoneNumberValidator(BaseModel):
    value: constr(min_length=4, max_length=16, pattern='^[0-9+ ]+$')
    
    @classmethod
    def prefix_check(cls, s:str) -> bool:
        if not s.startswith('+') or s.count('+') != 1:
            return False
        return True
    
    @classmethod
    def digit_check(cls, s:str) -> bool:
        return all(d.isdigit() or d == '+' for d in s)
    
    @classmethod
    def str_clean(cls, s:str) -> str:
        return s.replace(' ', '')

    @field_validator('value')
    def validate_phone(cls, v):
        if not cls.prefix_check(v):
            raise ValueError('Phone number has to start from + prefix')
        if not cls.digit_check(v):
            raise ValueError('Phone number must consist only digits')
        return cls.str_clean(v)
        