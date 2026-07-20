from datetime import datetime, timezone

from services.jwtService import _decode_jwt

def _get_role(a_token: str) -> str:
    payload = _decode_jwt(a_token)

    if payload and payload['role']:
        return payload['role']

def _get_datetime_now() -> datetime:
    return datetime.now(timezone.utc)

def unwrap(data: dict):
    res = dict()
    for key, val in data.items():
        res[key] = val['value']
    
    return res