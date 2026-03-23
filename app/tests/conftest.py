import asyncio

from collections.abc import (
    AsyncGenerator,
    Generator,
    Iterator,
)
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

import pytest
import pytest_asyncio

from testcontainers.postgres import PostgresContainer  # type: ignore

from app.db_connection import get_db
from app.main import app
from app.models.base import Base


@pytest.fixture(scope="session")
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
async def engine(
    postgres_container: PostgresContainer,
) -> AsyncGenerator[AsyncEngine, None]:
    """
    Создаем генератор сессии и таблицы в базе данных
    """
    engine = create_async_engine(
        postgres_container.get_connection_url(),
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.execute(
            text("CREATE SCHEMA IF NOT EXISTS bookings")
        )
        await conn.commit()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(
            text("DROP SCHEMA IF EXISTS bookings CASCADE")
        )
        await conn.commit()

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


@pytest.fixture
def test_client(
    engine: AsyncEngine,
) -> Generator[TestClient, None, None]:
    """
    Создание тестового клиента FastAPI с переопределением зависимости get_db
    """

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        """
        Переопределение зависимости для использования тестовой сессии
        """
        async_session = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
