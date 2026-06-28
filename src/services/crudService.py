from fastapi import FastAPI, HTTPException, Depends, Body, status, Cookie, File, UploadFile, APIRouter
from sqlalchemy.exc import SQLAlchemyError

from db.schema import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from models.client import ClientModel
from schemas.client import ClientSchema, UpdateInput

from sqlalchemy.orm.attributes import InstrumentedAttribute

from sqlalchemy.exc import IntegrityError, OperationalError, MultipleResultsFound
from datetime import datetime, timezone
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from cryptography.hazmat.backends import default_backend

from typing import Optional
from os import urandom
import base64
from core.config import setting
from services.jwtService import _tokens_validity, _decode_jwt, _check_token_expirity

#RBAC - Role Based Access Control User-Admin
# key = os.environ('SECRET_KEY').encode()
#decrypt messages each time I show them in GUI, do something with decryption key

#root_user: 0/1

#outer client add from random website visitor

cruds = APIRouter()

def client_crm(post_arg: ClientSchema, access_token_arg: Optional[str], refresh_token_arg: Optional[str], db_arg: Session) -> dict:

    if not _check_token_expirity(access_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Try to refresh it')
    
    if not _check_token_expirity(refresh_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Provide new credentials')

    encryption_key = _generate_bytes(32)
    encrypted_message = _encrypt_string(key=encryption_key, plaintext=post_arg.message.value)
    db_client = _compound_client_model(full_name=post_arg.full_name.value, email=post_arg.email.value, phone_number=post_arg.phone_number.value, message=encrypted_message)

    _upload_client_to_db(target=db_client, db=db_arg)
    
    return {"issued": datetime.now(tz=timezone.utc).isoformat()}

def edit_client_crm(post_arg: UpdateInput, access_token_arg: Optional[str], refresh_token_arg: Optional[str], db_arg: Session) -> dict:

    if not _check_token_expirity(access_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Try to refresh it')
    
    if not _check_token_expirity(refresh_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Provide new credentials')
    
    role = _get_user_role(access_token=access_token_arg)
    if not _verify_role(role):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='RBAC Denied')
    
    db_client = _get_client_by_uuid(db=db_arg, uuid=post_arg.value)

    now = _generate_current_datetime()
    _make_client_changes_to_db(target=db_client, db=db_arg, completed=True, date_completed=now)

    return {"issued": datetime.now(tz=timezone.utc).isoformat()}

def delete_client_crm(post_arg: UpdateInput, access_token_arg: Optional[str], refresh_token_arg: Optional[str], db_arg: Session) -> dict:

    if not _check_token_expirity(access_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Try to refresh it')
    
    if not _check_token_expirity(refresh_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Provide new credentials')
    
    role = _get_user_role(access_token=access_token_arg)
    if not _verify_role(role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='RBAC Denied')

    db_client = _get_client_by_uuid(db=db_arg, uuid=post_arg.value)

    _delete_client_from_db(db_client)

    return {"issued": datetime.now(tz=timezone.utc).isoformat()}

# def find_client_crm(access_token_arg: Optional[str], refresh_token_arg: Optional[str], db_arg: Session):

#     if not _check_token_expirity(access_token_arg):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Try to refresh it')
    
#     if not _check_token_expirity(refresh_token_arg):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Provide new credentials')
    
#     role = _get_user_role(access_token=access_token_arg)
#     if not _verify_role(role):
#             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='RBAC Denied')

#     db_client = filter_customers(post.input, parameter=predicate, database=db)

#     possible_ids = [item.id for item in search_result]
#     credentials = ' '.join([item.full_name for item in search_result])
#     result = [ClientSchema.from_orm(item) for item in search_result]

#     return {"issued": datetime.now(tz=timezone.utc).isoformat()}


def _encrypt_string(key: bytes, plaintext: str) -> str:
    bits = urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CFB(bits), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()

    return base64.b64encode(bits + ciphertext).decode('utf-8')

def _get_user_role(access_token: str) -> str:
    payload = _decode_jwt(access_token)

    if payload and payload['role']:
        return payload['role']

def _generate_bytes(num: int):
    return urandom(num)

def _generate_current_datetime():
    return datetime.now(timezone.utc)

def _verify_role(payload: dict) -> bool:
    return payload.get('role') == 'admin'

def _compound_client_model(full_name: str, email: str, message: str, phone_number: str) -> ClientModel:
    client = ClientModel(full_name=full_name, email=email, message=message, phone_number=phone_number)
    return client

def _upload_client_to_db(target: ClientModel, db: Session) -> None:
    try:
        db.add(target)
    except IntegrityError as E:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Something went wrong (Integrity) {E}")

    db.commit()
    db.refresh(target)

    return

def _make_client_changes_to_db(target: ClientModel, db: Session, **kwargs):
    try:
        for key, value in kwargs.items():
            setattr(target, key, value) 
    except IntegrityError:
        db.rollback()
        raise HTTPException()
    
    db.commit()
    db.refresh(target)

    return

def _get_client_by_uuid(db: Session, uuid: str) -> Optional[ClientModel]:
    try:
        instance = db.query(ClientModel).filter(ClientModel.id == uuid).first()
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Coldn't find client by provided data")
    
    return instance

def _delete_client_from_db(target: ClientModel, db: Session):
    try:
        db.delete(target)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Object is in use")
    db.commit()
    return

def _filter_customers(target: str, parameter: InstrumentedAttribute, database: Session) -> list[ClientModel]:
    try:
        found = database.query(ClientModel).filter(parameter == target).all()
        return found
    except IntegrityError:
        database.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Couldn't find client")
    
def _upload_encryption_key_to_db(key: str, datetime: datetime , db: Session):
    ...

