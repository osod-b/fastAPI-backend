
from fastapi import Depends, Cookie, APIRouter, UploadFile, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from db.schema import SessionLocal
from core.config import setting
from services.filesService import file_export, file_import


files = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@files.get('/files/export_file', response_class=FileResponse, status_code=status.HTTP_200_OK)
def export_file(file_format: str = 'excel', order_by: str = 'id', table_name: str = 'clients', access_token = Cookie(alias="access_token", default=None), refresh_token = Cookie(alias="refresh_token", default=None) , database: Session = Depends(get_db)):
    data = file_export(table_name_arg=table_name, file_format_arg=file_format, order_by_arg=order_by, access_token_arg=access_token, refresh_token_arg=refresh_token, db_arg=database)

    return FileResponse(path=data, status_code=status.HTTP_200_OK, media_type="application/octet-stream")

@files.get('files/import_file', status_code=status.HTTP_200_OK)
def import_file(file: UploadFile, access_token = Cookie(alias="access_token", default=None), refresh_token = Cookie(alias="refresh_token", default=None)):
    data = file_import(file_arg=file, access_token_arg=access_token, refresh_token_arg=refresh_token)

    response = JSONResponse(status_code=status.HTTP_200_OK, content=data)

    return response


