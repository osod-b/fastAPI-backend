from datetime import timezone, timedelta, datetime
from typing import Optional

from fastapi import HTTPException, status
from schemas.user import UserLogin, UserRegistration
from passlib.context import CryptContext
from cryptography.fernet import Fernet

from validators.users import VerificationalCode, PasswordValidator, EmailValidator
from utils.Repositories import UserRepository
from app.redis import redis_session
from core.config import setting
from services.jwtService import (
    _create_jwt, 
    _create_payload,
    _refresh_a_token,
)
from utils.authHelpers import (
    _crt_access_code,
    _mail_actv,
    _vrf_pwd,
    _hash_pwd,
    _lcase, 
    _vrf_pk,
    _vrf_acc,
    _vrf_rk,
)

# CLEANER CODE
# style helpers in the same consistent wa

key = setting.FERNET_KEY
cipher = Fernet(key)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

class UserSignupService:

    async def signup(   
            self,
            post: UserRegistration,
            uip: str,
            rep: UserRepository,
        ) -> dict:
        
        username, email = _lcase(post.username.value, post.email.value)
        password = post.password.value

        await rep._exists(username)
        await rep._exists(email)

        encrypted_pwd = cipher.encrypt(password.encode('utf-8'))
        code = _crt_access_code()

        redis_session.hset_exp(
            'user', 
            uip, 
            'register',
            mapping={
                    'access_code': code, 
                    'progress_key': 1,
                    'email': email,
                    'password': encrypted_pwd,
                    'username': username,
            },
            time=60 * 15,
            )
                                                                                                          
        return {"message": "Proceed to the next step",
                "code (test)": code,
                }

    async def mfa(
            self,
            post: VerificationalCode,
            uip: str,
            rep: UserRepository,
        ) -> tuple:

        code = post.value

        if not _vrf_rk(uip, 'register'):
            raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Verify redis Key')
    
        if not _vrf_pk(uip, 'register', 1):
            raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail='Verify progress Key')
    
        if not _vrf_acc(uip, 'register', code):
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Verify access Code')
        
        username = redis_session.hget('user', uip, 'register', 'username')
        email = redis_session.hget('user', uip, 'register', 'email')

        encrypted_pwd = redis_session.hget('user', uip, 'register', 'password')
        
        decrypted_pwd = cipher.decrypt(encrypted_pwd).decode('utf-8')

        hashed_pwd = _hash_pwd(pwd_context, decrypted_pwd)

        item = rep.build_model(username=username, email=email,
                               role='user', password=hashed_pwd,)

        uuid = str(await rep.upload_model(item, req_uuid=True))

        a_payload = _create_payload(**{'sub': uuid, 'name': username,
                                            'role': 'user', 'root': False})
        r_payload = _create_payload(**{'sub': uuid, 'name': username},
                                    refresh=True)

        a_token = _create_jwt(a_payload)
        r_token = _create_jwt(r_payload,
                              timedelta(hours=12), refresh=True)
        
        redis_session.hdel('user', uip, 'register')

        return (a_token, r_token)
    
    async def forgot_pwd(
            self,
            post: EmailValidator,
            uip: str, 
            rep: UserRepository,
        ) -> dict:

        email = post.value

        await rep._exists(email)

        item = await rep._get_by_email_or_none(email)
        active = item.active

        code = _crt_access_code()

        redis_session.hset_exp(
            'user',
            uip,
            'forgot_pwd',
            mapping={
                    'access_code': code,
                    'progress_key': 2,
                    'email': email,
                    'active': active,   
            },
            time = 60 * 15,
            )

        return {"message": "Password recovery request was sent",
                "code (test)": code,
                }
    
    async def vrf_code(
            self,
            post: VerificationalCode,
            uip: str,
            rep: UserRepository,
        ) -> dict:

        code = post.value

        if not _vrf_rk(uip, 'forgot_pwd'):
            raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Verify redis Key')
    
        if not _vrf_pk(uip, 'forgot_pwd', 2):
            raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail='Verify progress Key')
    
        if not _vrf_acc(uip, 'forgot_pwd', code):
            raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='Verify access Code')

        
        redis_session.set_hval('user', uip, 'forgot_pwd', 'progress_key', 3)

        return {"message": "Code was verified. Process to password change",
                "code (test)": code,
                }
    
    async def reset_pwd(
            self,
            post: PasswordValidator,
            uip: str,
            rep: UserRepository
        ) -> set:

        if not _vrf_rk(uip, 'forgot_pwd'):
            raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail='Verify redis Key')
    
        if not _vrf_pk(uip, 'forgot_pwd', 3):
            raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail='Verify progress Key')                           #what if someone trued to change redis values?

        password = post.value

        email = redis_session.hget('user', uip, 'forgot_pwd', 'email')
        active = redis_session.hget('user', uip, 'forgot_pwd', 'active')

        hashed_pwd = _hash_pwd(pwd_context, password)

        if active != 'True':
            await rep.update_by_attrs(email, password=hashed_pwd, active=True)
        else:
            await rep.update_by_attrs(email, password=hashed_pwd)
        
        redis_session.hdel('user', uip, 'forgot_pwd')
        
        return {"message":"Password was successfully changed"}

class UserLoginService:
    async def login(
            self,
            post: UserLogin,
            uip: str,
            rep: UserRepository,
        ) -> dict | tuple:

        identifier = _lcase(post.identifier.value)[0]

        if rep._identify_input(identifier) == 'email':
            item = await rep._get_by_email_or_none(identifier)
        elif rep._identify_input(identifier) == 'username':
            item = await rep._get_by_username_or_none(identifier)

        if not item:
            raise HTTPException(
                status_code=404, 
                detail="User doesn't exist",
            )

        active = item.active
        role = item.role
        root = item.root
        uuid = str(item.id)

        plain_pwd = post.password.value
        hashed_pwd = item.password

        if not _vrf_pwd(pwd_context, plain_pwd, hashed_pwd):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password Doesn't Match"
            )

        if not _mail_actv(active):
            code = _crt_access_code()
            redis_session.hset_exp(
                'user',
                uip, 
                'login',
                mapping={
                        'access_code': code,
                        'progress_key': 2,
                        'uuid': uuid,
                },
                time=60 * 15
            )
            
            return {"message":  "Proceed to the next step (Email Acitvation)"}
        
        else:
            a_payload = _create_payload(**{'sub': uuid, 'name': identifier,
                                           'role': role, 'root': root})
            r_payload = _create_payload(**{'sub': uuid, 'name': identifier},
                                        refresh=True)

            a_token = _create_jwt(a_payload)
            r_token = _create_jwt(r_payload,
                                  timedelta(hours=12), refresh=True)

            return (a_token, r_token)
    
    async def mfa(
            self,
            post: VerificationalCode,
            uip: str,
            rep: UserRepository,
        ) -> tuple:

        code = post.value

        if not _vrf_rk(uip, 'login'):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Verify redis Key')
    
        if not _vrf_pk(uip, 'login', 2):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Verify progress Key')                                               
        
        if not _vrf_acc(uip, 'login', code):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Verify access Code')

        uuid = redis_session.hget('user', uip, 'login', 'uuid')

        await rep.update_by_attrs(uuid, active=True)

        item = await rep._get_by_uuid_or_none(uuid)

        uname = item.username
        uuid = item.id
        role = item.role
        root = item.root

        a_payload = _create_payload(
                **{'sub': uuid, 'name': uname,
                'role': role, 'root': root})
        
        r_payload = _create_payload(
                **{'sub': uuid, 'name': uname},
                refresh=True)

        a_token = _create_jwt(a_payload)
        r_token = _create_jwt(r_payload,
                              timedelta(hours=12), refresh=True
                ) 

        redis_session.hdel('user', uip, 'login')

        return (a_token, r_token)

    async def refresh(
            self,
            a_token: Optional[str],
            r_token: Optional[str]
    ) -> tuple:
        result = _refresh_a_token(a_token, r_token)

        return result


