from services.authService import login, register, logout, forgot_pwd, vrf_code, reset_pwd, reg_mfa, refresh, login_mfa
from fastapi import APIRouter, Depends, Cookie, Request, status
from validators.users import VerificationalCode, EmailValidator, PasswordValidator
from schemas.user import UserLogin, UserRegistration
from datetime import datetime, timezone
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from db.schema import SessionLocal

auth = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#generate uuid in db model

#separate layers, build basic structure for endpoints, completly analyze and finish auth endpoints. Re read all and create understanding of system.

#TODO_: 
#account lock up after 3 bad attempts but lock out after page refresh
#after some certain verification's as log in autofill fields - remember me property (if remember me - create longer session or longer jwt expirity??)
#abstract email validation before registration
#account deactivation after 15 days logged out

#Bearer token, some issues with BucketRateLimiter, also analyze it.

#alternative concepts - maybe with async
#save somewhat like key in this relation, next step will be verifier endpoint where user will send his code
#this second endpoint takes this code insterted and then varifies it with the code in endpoint


@auth.post('/auth/login', status_code=status.HTTP_200_OK)
def login_user(post: UserLogin, request: Request, database: Session = Depends(get_db)):
    result = login(post_arg=post, request_arg=request, db_arg=database)
    if result:
        a_token, r_token = result

        response = JSONResponse(content = {"message": "Login successful. JWT Saved."})
        response.set_cookie(key="access_token", value=a_token, httponly=True, secure=True, samesite="strict", max_age=30*60)
        response.set_cookie(key="refresh_token", value = r_token, httponly=True, secure=True, samesite="strict", max_age=7*24*60*60)

        return response
    
    return JSONResponse(content={"message":"Code was sent, proceed further"}, status_code=status.HTTP_202_ACCEPTED)

@auth.post('/auth/login/activate_email', status_code=status.HTTP_200_OK)
def login_activate(code: VerificationalCode, request: Request, database: Session = Depends(get_db)):
    a_token, r_token = login_mfa(code_arg=code, request_arg=request, db_arg=database)
    
    response = JSONResponse(content = {"message": "Login successful. JWT Saved."})
    response.set_cookie(key="refresh_token", value=r_token, httponly=True, secure=True, samesite="strict", max_age=7*24*60*60)
    response.set_cookie(key="access_token", value=a_token, httponly=True, secure=True, samesite="strict", max_age=30*60)
    
    return response

@auth.post('/auth/refresh', status_code=status.HTTP_200_OK)
def refresh_session(access_token = Cookie(alias="access_token", default=None), refresh_token = Cookie(alias="refresh_token", default=None)):
    new_access_token = refresh(access_token_arg=access_token, refresh_token_arg=refresh_token)
    response = JSONResponse(content={"message":"JWT was updated successfully", "issued": datetime.now(timezone.utc)})
    response.set_cookie(key='access_token', value=new_access_token, httponly=True, secure=True, samesite="strict", max_age=7*24*60*60)

    return response

@auth.patch('/auth/logout', status_code=status.HTTP_200_OK)
def logout_user(access_token=Cookie(alias='access_token', default=None), refresh_token=Cookie(alias='refresh_token', default=None)):
    logout(access_token_arg=access_token, refresh_token_arg=refresh_token)
    
    response = JSONResponse(content={
        "issued": datetime.now(timezone.utc).isoformat(),
        "message": "Log out successfully"
    })
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response

@auth.post('/auth/register', status_code=status.HTTP_202_ACCEPTED)
def register_user(post: UserRegistration, request: Request, database: Session = Depends(get_db)):
    data = register(post_arg=post, request_arg=request, db_arg=database)

    return JSONResponse(content=data)
    
@auth.patch('/auth/register/verification', status_code=status.HTTP_200_OK)
def register_mfa(code: VerificationalCode, request:Request, database: Session = Depends(get_db)):
    data = reg_mfa(code_arg=code, request_arg=request, db_arg=database)
    data.update({"message": "Completed"})
    
    return JSONResponse(content=data)

@auth.post('/auth/forgot_password', status_code=status.HTTP_202_ACCEPTED)
def forgot_password(email: EmailValidator, request: Request, database: Session = Depends(get_db)):
    data = forgot_pwd(email_arg=email, request_arg=request, db_arg=database)
    data.update({'message': 'Completed'})

    return JSONResponse(content=data)

@auth.post('/auth/verify_code', status_code=status.HTTP_202_ACCEPTED)
def verify_code(code: VerificationalCode, request: Request):
    data = vrf_code(code_arg=code, request_arg=request)
    data.update({'message': 'Completed'}) 

    return JSONResponse(content=data)

@auth.post('/auth/reset_password', status_code=status.HTTP_200_OK)
def reset_password_user(password: PasswordValidator, request: Request, database: Session = Depends(get_db)):
    data = reset_pwd(password_arg=password, request_arg=request, db_arg=database)
    data.update({'message':'Completed'})

    return JSONResponse(content=data)