import asyncio

from collections.abc import (
    AsyncGenerator,
    Generator,
    Iterator,
)
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import pytest
import pytest_asyncio

from testcontainers.postgres import PostgresContainer  # type: ignore

from app.models.base import Base


@pytest.mark.asyncio(scope="session")
def event_loop_session() -> Generator[Any, Any, Any]:
    """
    Создает цикл событий для тестов
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container() -> Iterator[str]:
    """
    Запускает PostgreSQL-контейнер для тестов
    """
    with PostgresContainer(
        image="postgres:15-alpine",
        driver="asyncpg",
    ) as postgres:
        yield postgres


@pytest_asyncio.fixture(scope="session")
async def fill_up_db(
    server: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    """
    Создаем генератор сессии и таблицы в базе данных
    """
    engine = create_async_engine(
        server.get_connection_url(),
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def session(
    engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Создание сессии для работы с базой данных в тестах
    """
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()
