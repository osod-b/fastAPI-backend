from fastapi import APIRouter, Depends, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from validators.users import VerificationalCode
from utils.Repositories import UserRepository
from services.authService import UserLoginService
from schemas.user import UserLogin
from utils.authHelpers import  _get_ip_address
from services.jwtService import _tokens_presence
from db.schema import get_db, get_cache_db


login = APIRouter()

def get_user_repo(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

@login.post('/auth/login', status_code=status.HTTP_200_OK)
async def login_user(
    post: UserLogin,
    request: Request, 
    service: UserLoginService = Depends(), 
    repository: UserRepository = Depends(get_user_repo)
):      
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Already Logged In'
        )
        
    uip = _get_ip_address(request)
    result = await service.login(post, uip, repository)

    if isinstance(result, dict):
        response = JSONResponse(content=result)
    elif isinstance(result, tuple):
        a_token, r_token = result
        response = JSONResponse(
            content = {"message": "Successful Log In. JWT Saved"}
        )
        response.set_cookie(
            key="access_token", value=a_token, httponly=True,
            secure=True, samesite="strict", max_age=30 * 60
        )
        response.set_cookie(
            key="refresh_token", value = r_token, httponly=True,
            secure=True, samesite="strict", max_age=7*24 * 60*60
        )
    else:
        raise HTTPException(status_code=500,
                            detail="Unexpected result type from login service"
        )

    return response

@login.post('/auth/login/activate_email', status_code=status.HTTP_200_OK)
async def mfa_user(
    post: VerificationalCode,
    request: Request,
    service: UserLoginService = Depends(),
    repository: UserRepository = Depends(get_user_repo)
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail='Already Logged In'
        )
    
    uip = _get_ip_address(request)
    result = await service.mfa(post, uip, repository)

    a_token, r_token = result

    response = JSONResponse(
        content = {"message": "Successfuly Activated and Logged In. JWT Saved"}
    )
    response.set_cookie(
        key="access_token", value=a_token, httponly=True,
        secure=True, samesite="strict", max_age=30 * 60
    )
    response.set_cookie(
        key="refresh_token", value=r_token, httponly=True,
        secure=True, samesite="strict", max_age=7*24 * 60*60
    )
    
    return response

@login.post('/auth/logout', status_code=status.HTTP_200_OK)
async def logout_user(
    request: Request,
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Isn't Logged In"
        )
    
    response = JSONResponse(content = { "message": "Log Out." })
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response                                                             #deleted jwt cookies isn't providing complete log out

@login.post('/auth/refresh', status_code=status.HTTP_200_OK)                     #when is this function forced
async def refresh_session(
    request: Request,
    service: UserLoginService = Depends()
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Log in First"
        )
    
    a_token, r_token = await service.refresh(a_token, r_token)

    response = JSONResponse(
        content={ "message": "Successfull JWT Refresh." }
    )
    
    response.set_cookie(
        key='access_token', value=a_token, httponly=True,
        secure=True, samesite="strict", max_age=30 * 60
    )
    response.set_cookie(
        key="refresh_token", value=r_token, httponly=True,
        secure=True, samesite="strict", max_age=7*24 * 60*60
    )

    return response