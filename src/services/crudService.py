from fastapi import HTTPException
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.client import ClientSchema, EditInput
from utils.Repositories import ClientRepository
from app.redis import redis_session
from core.config import setting
# from logger import Logger
from utils.crudHelpers import unwrap
from validators.clients import UUIDVal

key = setting.FERNET_KEY
cipher = Fernet(key)

class ClientService():

    async def add(
            self,
            post: ClientSchema,
            rep: ClientRepository,

    ) -> dict:
        as_dict = post.model_dump(mode="json")
        as_dict_unw = unwrap(as_dict)

        encrypted_msg = cipher.encrypt(post.message.value.encode('utf-8')).decode('utf-8')
        as_dict_unw["message"] = encrypted_msg
        
        item = rep.build_model(**as_dict_unw)
        uuid = await rep.upload_model(item, req_uuid=True)

        uuid = str(uuid)
        pnum = item.phone_number
        email = item.email

        cache = redis_session.get_whole_hash('client', 'session', 'ratelimiter')
        if (
            cache and 
            cache['phone_number'] == pnum and
            cache['email'] == email
        ):
            raise HTTPException(status_code=409, detail="Same request sent too often")
            
        #instead of ip is better to use sessionid

        redis_session.hset_exp('client', 
                               'session', 
                               'ratelimiter',
                                mapping={
                                    'uuid': uuid,
                                    'phone_number': pnum,
                                    'email': email,
                                },
                                time=60 * 30)
       
        return {"message": "Client was uploaded"}
    
    async def update(
            self,
            post: EditInput,
            rep: ClientRepository,
    ) -> dict:

        as_dict = post.model_dump()
        as_dict_unw = unwrap(as_dict)

        if "message" in as_dict_unw["field"]:
            encrypted_msg = cipher.encrypt(as_dict_unw["value"])
            as_dict_unw["value"] = encrypted_msg

        uuid = str(as_dict_unw.pop("uuid"))
        attrs = {as_dict_unw["field"]: as_dict_unw["value"]}

        item = await rep._exists(uuid)

        await rep.update_by_attrs(item, **attrs)

        return {"message": "Client was updated"}
    
    async def delete(
            self,
            post: UUIDVal,
            rep: ClientRepository,
    ) -> dict:
        
        uuid = str(post.value)
        item = await rep.get_by_uuid_or_none(uuid)

        if not item:
            raise HTTPException(
                status_code=404, 
                detail="Record wasn't found",
            )
        
        await rep.delete_record(item)

        return {"message": "Client was deleted"}
    
    async def get_single(
            self,
            post: UUIDVal,
            rep: ClientRepository,
    ) -> dict:
        
        uuid = str(post.value)

        item = await rep.get_by_uuid_or_none(uuid)
        if item is None:
            raise HTTPException(status_code=404, detail="Client not found")
        
        dictionized = item.as_dict()
        uncrypted_msg = cipher.decrypt(dictionized["message"].encode('utf-8')).decode('utf-8')
        dictionized["message"] = uncrypted_msg
        dictionized["id"] = str(dictionized["id"])

        return {"message": "Client was found",
                "object": dictionized }
