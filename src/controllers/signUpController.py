from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security.http import HTTPAuthorizationCredentials, HTTPBearer

from validators.users import VerificationalCode, EmailValidator, PasswordValidator
from schemas.user import UserRegistration
from utils.Repositories import UserRepository
from services.authService import UserSignupService
from utils.authHelpers import  _get_ip_address
from services.jwtService import _tokens_presence
from db.schema import get_db


sign = APIRouter()

get_bearer_token = HTTPBearer(auto_error=False)

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

@sign.post('/auth/register', status_code=status.HTTP_202_ACCEPTED)
async def register_user(
    post: UserRegistration,
    request: Request,
    service: UserSignupService = Depends(),
    repository: UserRepository = Depends(get_user_repo)
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Log out first'
        )               

    uip = _get_ip_address(request)                                  #weird ip take
    result = await service.signup(post, uip, repository)

    response = JSONResponse(content=result)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response
    
@sign.patch('/auth/register/activate_email', status_code=status.HTTP_200_OK)
async def register_mfa(
    post: VerificationalCode,
    request:Request,
    service: UserSignupService = Depends(),
    repository: UserRepository = Depends(get_user_repo)
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Log out first'
        )     
    
    uip = _get_ip_address(request)

    result = await service.mfa(post, uip, repository)

    a_token, r_token = result

    response = JSONResponse(content={"message": "Successfull Registration and Auto Log In"})

    response.set_cookie(
        key="access_token", value=a_token, httponly=True,
        secure=True, samesite="strict", max_age=30 * 60
    )
    response.set_cookie(
        key="refresh_token", value=r_token, httponly=True,
        secure=True, samesite="strict", max_age=7*24 * 60*60
    )
    
    return response

@sign.post('/auth/forgot_password', status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    post: EmailValidator,
    request: Request,
    service: UserSignupService = Depends(),
    repository: UserRepository = Depends(get_user_repo)
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if _tokens_presence(a_token, r_token):
        raise HTTPException(status_code=
            status.HTTP_409_CONFLICT,
            detail='Log out first'
        )
    
    uip = _get_ip_address(request)
    result = await service.forgot_pwd(post, uip, repository)

    response = JSONResponse(content=result,
                            status_code=202
                            )
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response

@sign.post('/auth/verify_code', status_code=status.HTTP_202_ACCEPTED)
async def verify_code_pwd(
    post: VerificationalCode,
    request: Request,
    service: UserSignupService = Depends(),
    repository: UserRepository = Depends(get_user_repo)
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if _tokens_presence(a_token, r_token):
        raise HTTPException(status_code=
            status.HTTP_409_CONFLICT,
            detail='Log out first'
        )

    uip = _get_ip_address(request)
    result = await service.vrf_code(post, uip, repository)

    response = JSONResponse(content=result)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response

@sign.post('/auth/reset_password', status_code=status.HTTP_200_OK)
async def reset_password(
    post: PasswordValidator,
    request: Request,
    service: UserSignupService = Depends(),
    repository: UserRepository = Depends(get_user_repo)
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if _tokens_presence(a_token, r_token):
        raise HTTPException(status_code=
            status.HTTP_409_CONFLICT,
            detail='Log out first'
        )

    uip = _get_ip_address(request)
    result = await service.reset_pwd(post, uip, repository)

    response = JSONResponse(content=result)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

    return response