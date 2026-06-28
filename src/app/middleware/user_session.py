# import redis.asyncio as redis
# from redis import Redis
# from uuid import UUID, uuid4
# from datetime import timedelta, datetime
# from dataclasses import dataclass
# from core.config import setting
# from typing import Any, Dict
# import hmac

# # # @dataclass
# # class UserSession:
# #     def __init__(self):
# #         self.session_id: str
# #         self.uuid: UUID = self.__generate_uuid4()

# #         self.access_token: str
# #         self.refresh_token: str
# #         self.redis_storage: Redis

# #         self.metadata: Dict

# #         self.created_at: datetime = datetime.now()
# #         self.expires_at: timedelta = timedelta(minutes=30)

# #     def _generate_ssid(self):
# #         return 
    
# #     def __generate_uuid4(self):
# #         return uuid4()

# #     def _create_redis_session(self):
# #         ...

# #     def _end_session(self):
# #         ...


# class RedisStorageRelation:
#     def __init__(self, mins: int):
#         self.SESSION_TTL = timedelta(minutes=mins)
#         self.SESSION_COOKIE = setting.SESSION_COOKIE
#         self.redis: redis.Redis | None = None
#         self.time_created: datetime | None = None

#     async def initialize(self):
#         self.redis = self._create_client()
#         self.time_created = datetime.now()

#     def _create_client(self) -> redis.Redis:
#         return redis.Redis(
#             host="localhost",
#             port=6379,
#             decode_responses=True,
#         )

#     async def _check_and_refresh(self):
#         if self.time_created is None or self.redis is None:
#             raise RuntimeError("Call initialize() before using the store.")

#         if (datetime.now() - self.time_created) >= self.SESSION_TTL:
#             await self.redis.aclose()        
#             self.redis = self._create_client()
#             self.time_created = datetime.now()

#     async def insert(self, key: Any, value: Any) -> None:
#         await self._check_and_refresh()
#         await self.redis.set(key, value)

#     async def get(self, key: Any) -> Any:
#         await self._check_and_refresh()
#         return await self.redis.get(key)

#     async def close(self) -> None:
#         if self.redis:
#             await self.redis.aclose()
#             self.redis = None







