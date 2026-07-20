from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from services.crudService import ClientService
from utils.Repositories import ClientRepository
from schemas.client import ClientSchema
from validators.clients import UUIDVal
from services.jwtService import _decode_jwt, _tokens_presence
from db.schema import get_db, get_cache_db
from utils.crudHelpers import _get_role

#protection from duplicate customer requests - limit on 3 - redis will help

crud = APIRouter()

async def get_client_repo(
        db: AsyncSession = Depends(get_db)
) -> ClientRepository:
    return ClientRepository(db)

@crud.post('/crud/add_client', status_code=status.HTTP_200_OK)
async def add(
    post: ClientSchema,
    request: Request,
    service: ClientService = Depends(),
    repository: ClientRepository = Depends(get_client_repo),
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
                status_code=403,
                detail='LogIn First'
        )

    result = await service.add(post, repository)
    response = JSONResponse(content=result)

    return response

@crud.post('/crud/edit_client', status_code=status.HTTP_200_OK)
async def edit_client(
    post: UUIDVal,
    request: Request,
    service: ClientService = Depends(),
    repository: ClientRepository = Depends(get_client_repo),
):
    a_token, r_token = request.cookies.get('access_token'), request.cookies.get('refresh_token')

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
                status_code=403,
                detail='LogIn First'
        )
    
    role = _get_role(a_token)

    if role != 'manager':
        raise HTTPException(
                status_code=403,
                detail="No RBAC Rules"
        )

    result = await service.update(post, repository)
    response = JSONResponse(content=result)

    return response

@crud.delete('/crud/delete_client', status_code=status.HTTP_200_OK)
async def delete_client(
    post: UUIDVal,
    request: Request,
    service: ClientService = Depends(),
    repository: ClientRepository = Depends(get_client_repo),
):
    a_token, r_token = request.cookies.get("access_token"), request.cookies.get("refresh_token")

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
                status_code=403,
                detail="LogIn First"
        )
    
    role = _decode_jwt(a_token)['role']

    if role != 'manager':
        raise HTTPException(
                status_code=403,
                detail="No RBAC Rules"
        )

    result = await service.delete(post, repository)
    response = JSONResponse(content=result)
 
    return response

@crud.get('/crud/find/', status_code=status.HTTP_200_OK)
async def find_client(
    post: UUIDVal,
    request: Request,
    service: ClientService = Depends(),
    repository: ClientRepository = Depends(get_client_repo),
):
    a_token, r_token = request.cookies.get("access_token"), request.cookies.get("refresh_token")

    if not _tokens_presence(a_token, r_token):
        raise HTTPException(
                status_code=403,
                detail="LogIn First"
        )
    try:
        role = _decode_jwt(a_token)['role']
    except (KeyError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if role != 'manager':
        raise HTTPException(
                status_code=403,
                detail="No RBAC Rules"
        )

    result = await service.get_single(post, repository)
    response = JSONResponse(content=result)
 
    return response