from uuid import UUID, uuid4
from fastapi import Request
import mailtrap as mt
import secrets

from app.redis import redis_session


def _lcase(*credentials) -> tuple:
    return tuple(map(str.casefold, credentials))

def _mail_actv(state: bool) -> bool:
    return state

def _vrf_rk(ip: str, operation: str) -> bool:
    return bool(redis_session.get_whole_hash(name='user', ip=ip, operation=operation))

def _vrf_pk(ip: str, operation: str, alleged_key: int) -> bool:
    return int(redis_session.hget(name='user', ip=ip, operation=operation, inner_key='progress_key')) == alleged_key

def _vrf_acc(ip: str, operation: str, code: str) -> bool:
    return redis_session.hget(name='user', ip=ip, operation=operation, inner_key='access_code') == code

def _hash_pwd(context, password: str) -> str:
    return context.hash(password)

def _vrf_pwd(context, plain_pwd: str, hashed_pwd: str) -> bool:
    return context.verify(plain_pwd, hashed_pwd)

def _crt_access_code() -> str:
    return secrets.token_urlsafe(4)

def _crt_uuid4() -> UUID:
    return uuid4()


def _get_ip_address(request: Request) -> str:
    return request.headers['x-user-ip']


# def _encrypt_data(password: str) -> str:
#     ...

# def _decrypt_data(string: str) -> str:
#     ...

# def send_email(sub: str, message: str, cat: str, sender: str = "", reciever: str = ""):
#     mail = mt.Mail(sender=mt.Address(email=sender, name="Tax Service"), to=[mt.Address(email=reciever)], subject=sub, text=message, category=cat)
#     client = mt.MailtrapClient(token="").send(mail)
#     return

# def _prolong_token(arg):
#     ...


