import os

from validators.clients import FileType, FileVal
from core.config import setting
from models.client import ClientModel
from utils.Repositories import ClientRepository #may be pdata?
from utils.filesHelpsers import (
    _fol_exist,
    _normalize_file_type,
    _save_to_file,
    _make_dirs,
    _write_import,
    _cl_to_dicts,
    )


class FilesService():
    
    async def file_import(
        self, 
        post: FileVal,
    ) -> dict:
        
        file = post.value

        f_name = file.filename
        f_type = _normalize_file_type(f_name.rsplit('.')[-1])
        
        path = os.path.join(setting.STORAGE_PATH, 'imports', f_type)

        if not _fol_exist(path):
            _make_dirs(path)

        c_path = _write_import(file, path, f_name)

        f_name = os.path.basename(c_path)

        return {'path': path,
                'file_name': f_name}


    async def file_export(
            self, 
            post: FileType,
            rep: ClientRepository,
    ) -> dict:
        
        f_type = _normalize_file_type(post.value)

        path = os.path.join(setting.STORAGE_PATH, 'exports', f_type)

        if not _fol_exist(path):
            _make_dirs(path)

        db_records = await rep.get_all()
        clients = _cl_to_dicts(db_records)

        c_path = _save_to_file(path, clients)

        f_name = os.path.basename(c_path)

        return {'path': c_path, 
                'file_name': f_name}


