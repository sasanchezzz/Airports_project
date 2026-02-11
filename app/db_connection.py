from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import settings


db_engine = create_async_engine(
    url=settings.get_dsn,
    echo=True,
)

Async_session_local = async_sessionmaker(
    bind=db_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with Async_session_local() as session:
        try:
            yield session
        finally:
            await session.close()
