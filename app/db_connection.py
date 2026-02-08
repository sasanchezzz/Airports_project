import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv


load_dotenv()

DB_URL = os.getenv("db_info")

db_engine = create_async_engine(DB_URL, echo=True)
Async_session_local = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with Async_session_local() as session:
        try:
            yield session
        finally:
            await session.close()
