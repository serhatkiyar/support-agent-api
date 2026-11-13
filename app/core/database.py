from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import settings

SQL_ALCHEMY_URL = f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
engine = create_async_engine(SQL_ALCHEMY_URL)

local_session = async_sessionmaker(bind=engine, autoflush=False)


async def get_db():
    try:
        async with local_session as db:
            yield db
    finally:
        db.close()
