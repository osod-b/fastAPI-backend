from fastapi import HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from typing import Optional
from models.client import ClientModel
# from models.pdata import PdataModel
from sqlalchemy.orm import Session
from core.config import setting
from services.jwtService import _tokens_validity, _decode_jwt, _check_token_expirity
import os
import shutil
import pandas as pd
from datetime import datetime, timezone

def file_export(table_name_arg: str, file_format_arg: str, order_by_arg: str, access_token_arg: Optional[str], refresh_token_arg: Optional[str], db_arg: Session) -> dict:

    if not _check_token_expirity(access_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Try to refresh it')
    
    if not _check_token_expirity(refresh_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Provide new credentials')

    root, role = _get_user_permissions(access_token=access_token_arg)

    if not _verify_role(role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RBAC Denied")
    
    if not _verify_root(root):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RBAC Denied")

    if not _verify_file_format(file_f=file_format_arg):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='File format not allowed')

    if order_by_arg not in _get_sorting_attributes(table_name_arg):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Table isn't supported")

    model = _get_model_by_table(table_name_arg)

    if not model:
        raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail='Column not supported by model.')

    attribute = getattr(model, order_by_arg)

    folder_name = _get_exports_dir(file_format_arg)

    if not _check_path_existance(folder_name):
        _make_dir(folder_name)

    db_data = _make_query_to_db(model=model, order_by=attribute, db=db_arg)

    _resolve_export_format(folder_name, db_data, table_name_arg)


    folder_with_file = os.path.join(folder_name, f'{table_name_arg}.{file_format_arg}')
    base = os.path.basename(folder_with_file)

    return FileResponse(path=folder_with_file, filename=base, media_type='text/csv' , status_code=status.HTTP_200_OK)

    return {"issued": datetime.now(timezone.utc())}

def file_import(file_arg: UploadFile, access_token_arg: str, refresh_token_arg: str) -> dict:

    if not _check_token_expirity(access_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Try to refresh it')
    
    if not _check_token_expirity(refresh_token_arg):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The token expired. Provide new credentials')

    root, role = _get_user_permissions(access_token=access_token_arg)

    if not _verify_role(role):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RBAC Denied")
    
    if not _verify_root(root):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="RBAC Denied")

    if not file_arg:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File not sent")
    
    meta = _get_meta_from_file(file_arg)
    path = _get_imports_dir(meta['content-type'])

    if not _check_path_existance(path):
        _make_dir(path)

    if _check_file_existance(path, meta['file_name']):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='File exists')

    _open_write_file(target_file=file_arg, dir=path, file_name=meta['file_name'])

    return {"issued": datetime.now(timezone.utc).isoformat(), 'path': path, 'meta': meta}


def _resolve_export_format(path: str, query, table_name: str):
    base = os.path.basename(path)

    if base == 'csv':
        _write_to_csv(dir=path, data=query, encode='utf-8')

    if base == 'db':
        _copy_db(dest=path)

    if base == 'excel':
        _write_to_excel(dir=path, data=query, table_name=table_name)


def _make_query_to_db(model: object, order_by: str, db: Session):
    return db.query(model).order_by(order_by).all()

def _open_write_file(target_file: UploadFile, dir: str, file_name: str) -> None:

    file_w_location = os.path.join(dir, file_name)

    with open(file_w_location, 'wb') as created_file:
        target_file.file.seek(0)
        created_file.write(target_file.file.read())
     
def _write_to_csv(dir: str, encode: str, data) -> None:
    with open(dir, 'w+', encoding=encode) as file: 
        for item in data: 
            item = str(item)
            file.write(item + ' \n')
        file.flush()        

def _write_to_excel(dir: str, data: list, table_name: str) -> None:
    data_dict = [item.as_dict() for item in data]

    df = pd.DataFrame(data_dict)
    df.to_excel(dir, index=False, engine='openpyxl', sheet_name=table_name)

def _copy_db(dir: str, src: str = 'db/data.db'):
    shutil.copyfile(src, dir)

def _get_export_folder(file_format: str) -> str:
    if file_format in ['xlsx', 'xlsm']:
        return 'excel'
    return file_format

def _get_model_by_table(target: str) -> object:
    return {'client': ClientModel, 'pdata': PdataModel}.get(target)

def _get_sorting_attributes(table: str) -> list | None:
    return {'client': ClientModel.__table__.keys(), 'pdata': PdataModel.__table__.keys()}.get(table)

def _get_imports_dir(media_type: str) -> str:
    if not _verify_media_type(media_type):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='MEDIA NOT ALLOWED')
    
    parent_path = 'storage/imports'

    child_path = _get_interpreted_media(media_type)

    return os.path.join(parent_path, child_path)

def _get_exports_dir(file_format: str):
    parent_path = 'storage/exports'

    child_path = _get_export_folder(file_format)

    return os.path.join(parent_path, child_path, file_format)

def _get_filename(uploaded_file: UploadFile) -> dict | None:
    if uploaded_file:
        return {'file_name': uploaded_file.filename}
    return None

def _get_file_content_type(uploaded_file: UploadFile) -> dict | None:
    if uploaded_file:
        return {'content_type': uploaded_file.content_type}
    return None

def _get_size_of_file(uploaded_file: UploadFile) -> dict | None:
    
    uploaded_file.file.seek(0, os.SEEK_END)
    size = uploaded_file.file.tell()
    uploaded_file.file.seek(0)

    return {'file_size': size}
    
def _get_user_permissions(access_token: str):
    payload = _decode_jwt(access_token)
    
    if payload and payload['role'] and payload['root']:
        return (payload['role'], payload['root'])

def _get_meta_from_file(file: UploadFile) -> dict:       
    operations = [_get_size_of_file, _get_filename, _get_file_content_type]
    meta = {}
    for f in operations:
        value = f(uploaded_file=file)
        if value:
            meta.update(value)
        else:
            meta.update({'Error':'Failed to get meta'})

    return meta
        
def _get_interpreted_media(target: str) -> str | None:
    return {'text/csv': 'csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'excel',
            'application/vnd.ms-excel.sheet.macroEnabled.12': 'excel', 'application/octet-stream': 'db'}.get(target)

def _verify_role(role: str) -> bool:
    return role == 'admin'

def _verify_root(root: bool) -> bool:
    return root == True

def _verify_file_format(file_f: str) -> bool:
    return file_f in setting.ALLOWED_FILE_FORMATS

def _verify_media_type(target: str) -> bool:
    return target in setting.ALLOWED_MEDIA

def _check_file_existance(path: str, file_name : Optional[str] = None) -> bool:
    if file_name:
        concatenated_path = os.path.join(path, file_name)
        return os.path.exists(concatenated_path)
    else:
        return os.path.exists(path)

def _check_path_existance(path: str) -> bool:
    return os.path.exists(path)

def _make_dir(path: str) -> bool:
    return os.makedirs(path)



def get_hashing_key():
    ...
