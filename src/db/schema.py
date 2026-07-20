from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import sqlalchemy.orm as _orm

from core.config import setting


main_engine = create_async_engine(setting.DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(autoflush=False, bind=main_engine, expire_on_commit=False, class_=AsyncSession)
Base = _orm.declarative_base()

cache_engine = create_async_engine(setting.CACHE_DB_URL, echo=True)
CacheSessionLocal = async_sessionmaker(autoflush=False, bind=cache_engine, expire_on_commit=False, class_=AsyncSession)
CacheBase = _orm.declarative_base()

async def init_db():
    async with main_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with cache_engine.begin() as conn:
        await conn.run_sync(CacheBase.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_cache_db():
    async with CacheSessionLocal() as session:
        yield session
