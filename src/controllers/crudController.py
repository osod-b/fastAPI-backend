from fastapi import APIRouter, HTTPException, status, Cookie, Depends, Request, Response
from services.crudService import client_crm, edit_client_crm, delete_client_crm

from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session
from db.schema import SessionLocal
from services.crudService import client_crm


crud = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#create logic for adding the completion date and count it for later showing
#change responses they expose too many things
#fix encryption of message

#protection of duplicate customer requests - limit on 3

@crud.post('/crud/add_client', status_code=status.HTTP_200_OK)
def create_client(access_token = Cookie(alias="access_token", default=None), refresh_token = Cookie(alias="refresh_token", default=None), database: Session = Depends(get_db)):
    data = client_crm(access_token_arg=access_token, refresh_token_arg=refresh_token, db_arg=database)
    data.update({"message":"Client was inserted"})

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

@crud.post('/crud/edit_client', status_code=status.HTTP_200_OK)
def edit_client(access_token = Cookie(alias="access_token", default=None), refresh_token = Cookie(alias="refresh_token", default=None), database: Session = Depends(get_db)):
    data = edit_client_crm(access_token_arg=access_token, refresh_token_arg=refresh_token, db_arg=database)
    data.update({"message":"Client was inserted"})

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

@crud.delete('/crud/delete_client', status_code=status.HTTP_200_OK)
def delete_client(access_token = Cookie(alias="access_token", default=None), refresh_token = Cookie(alias="refresh_token", default=None), database: Session = Depends(get_db)):
    data = delete_client_crm(access_token_arg=access_token, refresh_token_arg=refresh_token, db_arg=database)
    data.update({"message":"Client was inserted"})

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)

@crud.get('/crud/find', status_code=status.HTTP_200_OK)
def find_client(email: str, phone_num: str, access_token = Cookie(alias="access_token", default=None), refresh_token = Cookie(alias="refresh_token", default=None), database: Session = Depends(get_db)):


    data = filter_client_crm(access_token_arg=access_token, refresh_token_arg=refresh_token, db_arg=database)
    data.update({"message":"Client was inserted"})

    return JSONResponse(status_code=status.HTTP_200_OK, content=data)