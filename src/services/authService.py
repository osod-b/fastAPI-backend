from services.jwtService import _create_jwt, _create_refresh_jwt, _jwt_payload_schema, _refresh_access_token, _tokens_validity
from fastapi import HTTPException, status, Request
from sqlalchemy.exc import IntegrityError, OperationalError
from schemas.user import UserLogin, UserRegistration
from datetime import timezone, timedelta, datetime
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models.user import UserModel
from app.redis import r_s
from sqlalchemy import or_
import mailtrap as mt
import secrets
from uuid import UUID, uuid4
import json

from app.redis import r_s

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

#CLEANER CODE
#style helpers in the same consistent way

def login(post_arg: UserLogin, request_arg: Request, db_arg: Session) -> tuple | None:
    
    if _tokens_validity(request_arg.cookies.get('access_token'), request_arg.cookies.get('refresh_token')):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Collission spotted. Log out first')

    user_ip = _get_ip_address(request_arg)

    identifier = _normalize(post_arg.identifier.value)[0]
    db_user = _get_user_by_context(username=identifier, email=identifier, db=db_arg)

    if not _verify_passwords(argument_pwd=post_arg.password.value, hashed_pwd=db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Passwords don't match")
    
    if db_user.active:
        a_payload = _jwt_payload_schema(sub=str(db_user.id), name=db_user.username, role=db_user.role, root=db_user.root)
        access_token = _create_jwt(payload=a_payload)
        
        r_payload = _jwt_payload_schema(ref=True, sub=str(db_user.id), name=db_user.username)
        refresh_token = _create_refresh_jwt(payload=r_payload, expires_delta=timedelta(hours=12))

        return (access_token, refresh_token)
    else:
        generated_code = _generate_random_verificational_code()
        r_s.set_hash_with_time_expirity(name='user', ip=user_ip, operation='login', time=60*15,mapping={'access_code':f'{generated_code}','progress_key':1,
                                                                                                        'user_object': json.dumps(db_user.as_dict())})
        
        return

def login_mfa(code_arg: str, request_arg: Request, db_arg: Request) -> tuple:
    user_ip = _get_ip_address(request_arg)

    if not _verify_redis_key(ip=user_ip, operation='login'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='1')
    
    if not _verify_progress_key(ip=user_ip, alleged_key=1, operation='login'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='2')

    if not _verify_access_code(ip=user_ip, code=code_arg.value, operation='login'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='3')
    
    user = r_s.get_single_value(name='user', ip=user_ip, operation='login', inner_key='user_object')
    user = json.loads(user)

    db_user = _get_user_by_context(username=user['username'], db=db_arg)
    _make_user_changes_to_db(target=db_user, db=db_arg, active=True)

    a_payload = _jwt_payload_schema(sub=user['id'], name=user['username'], role=user['role'], root=user['root'])
    access_token = _create_jwt(payload=a_payload)
    
    r_payload = _jwt_payload_schema(ref=True, sub=user['id'], name=user['username'])
    refresh_token = _create_refresh_jwt(payload=r_payload, expires_delta=timedelta(hours=12)) 

    r_s.clean_hash_by_key(name='user', ip=user_ip, operation='login')

    return (access_token, refresh_token)

def logout(access_token_arg: Optional[str], refresh_token_arg: Optional[str]):
    if not _tokens_validity(access_token_arg, refresh_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User never been issued')
    return 
   
def register(post_arg: UserRegistration, request_arg: Request, db_arg: Session) -> set:

    if _tokens_validity(request_arg.cookies.get('access_token'), request_arg.cookies.get('refresh_token')):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Collission spotted. Log out first')

    user, email = _normalize(post_arg.username.value, post_arg.email.value)
    _user_presence(username=user, email=email, db=db_arg)

    user_ip = _get_ip_address(request_arg)
    generated_code = _generate_random_verificational_code()

    r_s.set_hash_with_time_expirity(name='user', ip=user_ip, operation='register', time=60*15, mapping={'access_code':f'{generated_code}', 'user_object':post_arg.model_dump_json(), 
                                                                                                          'progress_key': 1})
    return {"issued": datetime.now(timezone.utc).isoformat()}

def reg_mfa(code_arg: str, request_arg: Request, db_arg: Session):
    user_ip = _get_ip_address(request_arg)

    if not _verify_redis_key(ip=user_ip, operation='register'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='r_key')
    
    if not _verify_progress_key(alleged_key=1, ip=user_ip, operation='register'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='p_key')
    
    if not _verify_access_code(code=code_arg.value, ip=user_ip, operation='register'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='a_c')
    
    user = UserRegistration.model_validate_json(r_s.get_single_value(name='user', ip=user_ip, operation='register', inner_key='user_object'))

    username, email, set_role = _normalize(user.username.value, user.email.value, 'user')

    password_hash = _hash_password_context(user.password.value)
    generated_uuid = _generate_uuid4()

    transformed = _compound_user_model(username=username, email=email, role=set_role, password_hash=password_hash, uuid=generated_uuid)
    _upload_user_to_db(target=transformed, db=db_arg)

    r_s.clean_hash_by_key(name='user', ip=user_ip, operation='register')

    return {"issued": datetime.now(timezone.utc).isoformat()}
    
def forgot_pwd(email_arg: str, db_arg: Session, request_arg: Request) -> dict:

    if _tokens_validity(request_arg.cookies.get('access_token'), request_arg.cookies.get('refresh_token')):
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Method not allowed, user is logged in')

    user_ip = _get_ip_address(request_arg)
    db_user = _get_user_by_context(db=db_arg, email=email_arg.value)

    generated_code = _generate_random_verificational_code()

    r_s.set_hash_with_time_expirity(name='user', ip=user_ip, operation='forgot_pwd', time = 60*15, mapping={'access_code': generated_code,'email': email_arg.value,'progress_key': 1})

    return {'issued': datetime.now(timezone.utc).isoformat()}

def vrf_code(code_arg: str, request_arg: Request) -> set:
    user_ip = _get_ip_address(request_arg)

    if not _verify_redis_key(ip=user_ip, operation='forgot_pwd'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='r_key')
    
    if not _verify_progress_key(alleged_key=1, ip=user_ip, operation='forgot_pwd'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='p_key')
    
    if not _verify_access_code(code=code_arg.value, ip=user_ip, operation='forgot_pwd'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='a_c')
    
    r_s.set_single_hash_value(name='user', ip=user_ip, operation='forgot_pwd', inner_key='progress_key', value= 2)

    return {'issued': datetime.now(timezone.utc).isoformat()}

def reset_pwd(password_arg: str, request_arg: Request , db_arg: Session) -> set:
    user_ip = _get_ip_address(request_arg) 

    if not _verify_redis_key(ip=user_ip, operation='forgot_pwd'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='r_key')
    
    if not _verify_progress_key(alleged_key=2, ip=user_ip, operation='forgot_pwd'):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='p_key')
    
    client_email = r_s.get_single_value(name='user', ip=user_ip, operation='forgot_pwd', inner_key='email')

    db_user = _get_user_by_context(db=db_arg, email=client_email)
    hashed_password = _hash_password_context(password_arg.value)
    _make_user_changes_to_db(target=db_user, db=db_arg, password=hashed_password)

    if not db_user.active:
        _make_user_changes_to_db(target=db_user, db=db_arg, active=True)
    
    r_s.clean_hash_by_key(name='user', ip=user_ip, operation='forgot_pwd')
    
    return {'Completed': datetime.now(timezone.utc).isoformat()}

def refresh(access_token_arg: Optional[str], refresh_token_arg: Optional[str]) -> str:
    if not _tokens_validity(access_token_arg, refresh_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User never been issued')

    refreshed_access_token = _refresh_access_token(a_token=access_token_arg, r_token=refresh_token_arg)

    return refreshed_access_token

def _verify_redis_key(ip: str, operation: str) -> bool:
    return bool(r_s.get_whole_hash(name='user', ip=ip, operation=operation))

def _verify_progress_key(ip: str, operation: str, alleged_key: int) -> bool:
    return int(r_s.get_single_value(name='user', ip=ip, operation=operation, inner_key='progress_key')) == alleged_key

def _verify_access_code(ip: str, operation: str, code: str) -> bool:
    return r_s.get_single_value(name='user', ip=ip, operation=operation, inner_key='access_code') == code

def _verify_passwords(argument_pwd: str, hashed_pwd: str) -> bool:
    return pwd_context.verify(argument_pwd, hashed_pwd)

def _hash_password_context(password: str) -> str:
    return pwd_context.hash(password)

def _get_ip_address(request: Request) -> str:
    return request.headers['x-user-ip']

def _normalize(*credentials) -> tuple:
    return tuple(map(str.casefold, credentials))

def _generate_random_verificational_code() -> str:
    return secrets.token_urlsafe(4)

def _generate_uuid4() -> UUID:
    return uuid4()

def _generate_email(sub: str, message: str, cat: str, sender: str = "hello@demomailtrap.co", reciever: str = "ripplehkg@gmail.com"):
    mail = mt.Mail(sender=mt.Address(email=sender, name="Tax Service"), to=[mt.Address(email=reciever)], subject=sub, text=message, category=cat)
    client = mt.MailtrapClient(token="a8d01dcb0d3951256ae216dda3d4f096").send(mail)
    return 

def _prolong_token(arg):
    ...

def _upload_user_to_db(target: UserModel, db: Session) -> None:
    try:
        db.add(target)
    except IntegrityError as E:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Something went wrong (Integrity) {E}")
    
    db.commit()
    db.refresh(target)

    return

def _make_user_changes_to_db(target: UserModel, db: Session, **kwargs) -> None:
    try:
        for key, value in kwargs.items():
            setattr(target, key, value) 
    except IntegrityError:
        db.rollback()
        raise HTTPException()
    
    db.commit()
    db.refresh(target)

    return

def _compound_user_model(uuid: UUID, username: str, email: str, role: str, password_hash: str) -> UserModel:
    user_model = UserModel(id = uuid, username = username, email = email, password = password_hash, role = role, root = False, active = True)
    
    return user_model

def _get_user_by_context(db: Session, username: str | None = None, email: str | None = None, ignore=True) -> Optional[UserModel]:
    if not ignore:
        try:
            instance = db.query(UserModel).filter(or_(UserModel.username == username, UserModel.email == email)).first()
        except OperationalError:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Coldn't find user by provided data")
        if not instance:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Couldn't find user")
        
        return instance
    else:
        instance = db.query(UserModel).filter(or_(UserModel.username == username, UserModel.email == email)).first()
        return instance

def _user_presence(username: str, email: str, db: Session) -> UserModel:

    if _get_user_by_context(username=username, db=db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
    
    if _get_user_by_context(email=email, db=db):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already taken") 