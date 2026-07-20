
from fastapi import Depends, APIRouter, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from services.filesService import FilesService
from sqlalchemy.ext.asyncio import AsyncSession

from utils.Repositories import ClientRepository
from validators.clients import FileVal, FileType
from services.jwtService import _tokens_presence
from utils.crudHelpers import _get_role
from db.schema import get_db


files = APIRouter()

async def get_client_repo(
        db: AsyncSession = Depends(get_db)
) -> ClientRepository:
    return ClientRepository(db)


#so far it just saves the data into a folder, later it modifies the db
@files.get('files/import_file', status_code=status.HTTP_200_OK)
async def file_import(
    post: FileVal,
    request: Request,
    service: FilesService = Depends(),
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=402,
            detail="Not Allowed"
        )
    
    if _get_role(a_token) != 'manager':
        raise HTTPException(
            status_code=402,
            detail="Not allowed"
        )
    
    result = await service.file_import(post)
    response = JSONResponse(content=result)

    return response

@files.get('/files/export_file', response_class=FileResponse, status_code=status.HTTP_200_OK)
async def file_export(
    post: FileType,
    request: Request, 
    service: FilesService = Depends(),
    repository: ClientRepository = Depends(get_client_repo),
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
            status_code=402,
            detail="Not Allowed"
        )
    
    if _get_role(a_token) != 'manager':
        raise HTTPException(
            status_code=402,
            detail="Not allowed"
        )

    result = await service.file_export(post, repository)
    response = FileResponse(path=result['path'],
                            filename=result['file_name'])

    return response


