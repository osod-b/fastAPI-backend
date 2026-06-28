from pydantic import BaseModel


class JWTResponse(BaseModel):
    token_type: str
    access_token: str
    refresh_token: str
    