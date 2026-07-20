from typing import Annotated, Any, Optional, List
import re

from sqlalchemy.exc import OperationalError, IntegrityError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from sqlalchemy import select
from uuid import UUID

from models.user import UserModel
from models.client import ClientModel


class UserRepository:
    
    def __init__(self, db: AsyncSession):
        self.db = db 

    async def _get_by_email_or_none(self, email: str) -> Optional[UserModel]:
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.email == email)
            )
        except OperationalError:
            raise HTTPException(503, detail="DB is down")
        return result.scalar_one_or_none()

    async def _get_by_username_or_none(self, username: str) -> Optional[UserModel]:
        try:
            result = await self.db.execute(
                select(UserModel).where(UserModel.username == username)
            )
        except OperationalError:
            raise HTTPException(503, detail="DB is down")
        return result.scalar_one_or_none()

    async def _get_by_uuid_or_none(self, uuid: str) -> Optional[UserModel]:
        try:
            uuid = UUID(uuid)
            result = await self.db.execute(
                select(UserModel).where(UserModel.id == uuid)
            )
        except OperationalError:
            raise HTTPException(503, detail="DB is down")
        return result.scalar_one_or_none()
    
    async def upload_model(self, object: UserModel, req_uuid: bool = False) -> Any:
        try:
            self.db.add(object)

            await self.db.commit()
            await self.db.refresh(object)
        except OperationalError:
            await self.db.rollback()
            raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="DB is down"
            )
        except TimeoutError:
            await self.db.rollback()
            raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Connection pool exhausted"
            )
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'{e}'
            )
        
        if req_uuid:
            return object.id

    async def update_by_attrs(self, identifier: str, **kwargs):
        input_type = self._identify_input(identifier)

        if input_type == "email":
            item = await self._get_by_email_or_none(identifier)
        elif input_type == "username":
            item = await self._get_by_username_or_none(identifier)
        else:
            item = await self._get_by_uuid_or_none(identifier)

        if not item:
            raise HTTPException(404,
                detail='User not found'
            )
        
        for key, value in kwargs.items():
            setattr(item, key, value)
        try:
            await self.db.commit()
            await self.db.refresh(item)
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT,
                detail="Update conflicts with existing data"
            )
        except OperationalError:
            await self.db.rollback()
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="DB is down"
            )

    async def _exists(self, indentifier: str):
        input_type = self._identify_input(indentifier)
        
        if input_type == "email":
            if await self._get_by_email_or_none(indentifier):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already taken"
                )
        elif input_type == "username":
            if await self._get_by_username_or_none(indentifier):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="Username already taken"
                )
        else:
            if await self._get_by_uuid_or_none(indentifier):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, 
                    detail="User with such UUID exists"
                )
            
    def build_model(self, **kwargs) -> UserModel:
        item = UserModel()
        combined = {**{'root': False, 'active': True},
                    **kwargs}

        for key, value in combined.items():
            setattr(item, key, value)

        return item
    
    def _identify_input(self, indentifier: str) -> Annotated[str, 'Input Type']:
        r_mail = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        r_uname = r'^[a-zA-Z]{3,}$'
        if re.match(r_mail, indentifier):
            return "email"
        elif re.match(r_uname, indentifier):
            return "username"
        else:
            try:
                UUID(indentifier)
                return "uuid"
            except (ValueError, AttributeError):
                pass
        
class ClientRepository:
    def __init__(self, async_db_session: AsyncSession):
        self.db = async_db_session

    async def upload_model(self, object: ClientModel, req_uuid: bool = False):
        try:
            self.db.add(object)

            await self.db.commit()
            await self.db.refresh(object)
        except OperationalError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="DB is down"
            )
        except TimeoutError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Connection pool exhausted"
            )
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'{e}'
            )
        
        if req_uuid:
            return object.id
    
    async def get_all(self) -> List[ClientModel]:
            result = self.db.execute(
                select(ClientModel)
            )
            
            return result.scalars().all()

    async def update_by_attrs(self, obj: ClientModel, **kwargs):
        
        for key, value in kwargs.items():
            setattr(obj, key, value)
        try:
            await self.db.commit()
            await self.db.refresh(obj)
        except OperationalError:
            await self.db.rollback()
            raise HTTPException(
                    status_code=503,
                    detail="DB is down"
            )
        except IntegrityError as e:
            await self.db.rollback()
            raise HTTPException(
                    status_code=503,
                    detail=f"{e}"
            )
    
    async def delete_record(self, object: ClientModel):
        try:
            await self.db.delete(object)
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()

            raise HTTPException(
                status_code=503, 
                detail=f'{e}'
            )
        except OperationalError as e:
            await self.db.rollback()

            raise HTTPException(
                status_code=503, 
                detail=f'{e}'
            )

    def build_model(self, **kwargs) -> ClientModel:
        item = ClientModel()

        for key, value in kwargs.items():
            setattr(item, key, value)

        return item
    
    async def get_by_uuid_or_none(self, uuid: str) -> Optional[ClientModel]:
        try:
            uuid = UUID(uuid)
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=204,
                detail="Not Valid UUID")
        try:
            result = await self.db.execute(
                select(ClientModel).where(ClientModel.uuid == uuid)
            )
        except OperationalError:
            raise HTTPException(503, detail="DB is down")

        return result.scalar_one_or_none()
        
    async def _exists(self, identifier: str) -> ClientModel:
        item = await self.get_by_uuid_or_none(identifier)
        if not item:
            raise HTTPException(
                status_code=404,
                detail="Resource not found"
            )
        return item
