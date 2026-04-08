from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest
import pytest_asyncio

from app.models.models import Aircrafts


@pytest_asyncio.fixture
async def test_aircrafts(session: AsyncSession) -> Aircrafts:
    """
    Создание тестовых данных для таблицы Aircrafts
    """
    aircraft = Aircrafts(
        aircraft_code="773", model="Boeing 777-300", range=11100
    )

    session.add(aircraft)
    await session.commit()
    await session.refresh(aircraft)
    return aircraft


@pytest.mark.asyncio
class TestReadAircraft:
    """
    Тесты для GET /aircrafts/{aircraft_code}
    """

    async def test_read_aircraft_success(
        self,
        async_client: AsyncClient,
        test_aircrafts: Aircrafts,
    ) -> None:
        """
        Тест успешного получения информации о самолете по коду.

        Проверяет:
        - Статус код 200
        - Корректность возвращаемых данных
        - Соответствие полей модели
        """
        response = await async_client.get(
            f"/aircrafts/{test_aircrafts.aircraft_code}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["aircraft_code"] == test_aircrafts.aircraft_code
        assert data["model"] == test_aircrafts.model
        assert data["range"] == test_aircrafts.range

        assert "aircraft_code" in data
        assert "model" in data
        assert "range" in data
