import os
import csv
import shutil
from datetime import datetime
from typing import List

from fastapi import UploadFile
import pandas as pd

from core.config import setting
from models.client import ClientModel


def _get_size_of_file(uploaded_file: UploadFile) -> dict | None:
    
    uploaded_file.file.seek(0, os.SEEK_END)
    size = uploaded_file.file.tell()
    uploaded_file.file.seek(0)

    return {'file_size': size}

def _get_fname(file: UploadFile) -> dict | None:
    return file.filename

def _get_fct(file: UploadFile) -> dict | None:
    return file.filename
        
def _make_fname():
    return datetime.now().strftime('%Y-%m-%d-%H:%M:%S')

def _fol_exist(path: str) -> bool:
    return os.path.exists(path)

def _make_dirs(path: str) -> bool:
    return os.makedirs(path)

def _normalize_file_type(f_type: str) -> str:
    if f_type in {'xlsx', 'xls'}:
            return 'excel'
    return f_type

def _cl_to_dicts(
        data: List[ClientModel]
) -> List[dict]:
    return [item.as_dict() for item in data]

def _save_to_file(
        path: str, 
        data: List[dict]
    ) ->  str:
    f_type = os.path.basename(path)
    
    return {'csv': _write_csv(path, data),
            'db': _write_db(path, data), 
            'excel':_write_excel(path, data)}[f_type]

def _write_import(
        file: UploadFile, 
        path: str, 
        f_name: str
    ) -> str:

    c_path = os.path.join(path, f_name)

    if os.path.exists(c_path):
        raise FileExistsError(f"File already exists: {c_path}")

    with open(c_path, 'wb') as o_file:
        content = file.read()
        o_file.write(content)

    return c_path

def _write_csv(
        path: str, 
        data: List[dict]
    ) -> str:
    file_name = _make_fname() + '.csv'
    c_path = os.path.join(path, file_name)


    with open(c_path, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    return c_path

def _write_excel(
        path: str, 
        data: List[dict], 
    ) -> str:
    file_name = _make_fname() + '.xlsx'
    c_path = os.path.join(path, file_name)

    df = pd.DataFrame(data)
    df.to_excel(c_path, index=False, engine='openpyxl', sheet_name='Clients')

    return c_path

def _write_db(path: str) -> str:
    file_name = _make_fname() + '.db'
    
    c_path = os.path.join(path, file_name)
    src = os.path.join(setting.STORAGE_PATH, 'files', 'data.db')
    try:
        shutil.copyfile(src, path)
    except Exception as e:
        raise ValueError(f'{e}')
    
    return c_path
     