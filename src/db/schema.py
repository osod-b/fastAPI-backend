import os
import sqlalchemy as _sql
import sqlalchemy.orm as _orm
from core.config import setting

main_engine = _sql.create_engine(setting.DATABASE_URL, connect_args={"check_same_thread": False}, echo=True)
SessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=main_engine)
Base = _orm.declarative_base()


cache_engine = _sql.create_engine(setting.CACHE_DB_URL, connect_args={"check_same_thread": False}, echo=True)
CacheSessionLocal = _orm.sessionmaker(autocommit=False, autoflush=False, bind=cache_engine)
CacheBase = _orm.declarative_base()

Base.metadata.create_all(bind=main_engine)

CacheBase.metadata.create_all(bind=cache_engine)