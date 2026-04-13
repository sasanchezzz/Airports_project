from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import Aircrafts


@pytest_asyncio.fixture
async def test_aircrafts_v2(session: AsyncSession) -> Aircrafts:
    """
    Создание тестовых данных для таблицы Aircrafts (v2)
    """
    aircraft = Aircrafts(
        aircraft_code="773", model="Boeing 777-300", range=11100
    )

    session.add(aircraft)
    await session.commit()
    await session.refresh(aircraft)
    return aircraft


class TestCreateAircraft:
    """
    Тесты для POST /aircrafts/add_aircraft
    """

    async def test_create_aircraft_success(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест успешного создания самолета.

        Проверяет:
        - Статус код 200
        - Корректность возвращаемых данных
        """
        payload = {
            "aircraft_code": "SU9",
            "model": "Sukhoi SuperJet-100",
            "range": 3000,
        }

        response = await async_client.post(
            "/api/v2/aircrafts/add_aircraft", json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert data["aircraft_code"] == "SU9"
        assert data["model"] == "Sukhoi SuperJet-100"
        assert data["range"] == 3000

    async def test_create_aircraft_duplicate_code(
        self,
        async_client: AsyncClient,
        test_aircrafts_v2: Aircrafts,
    ) -> None:
        """
        Тест создания самолета с существующим кодом.

        Проверяет:
        - Статус код 400
        - Сообщение об ошибке
        """
        payload = {
            "aircraft_code": "773",
            "model": "Boeing 777-300",
            "range": 11100,
        }

        response = await async_client.post(
            "/api/v2/aircrafts/add_aircraft", json=payload
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    async def test_create_aircraft_invalid_range(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест создания самолета с невалидной дальностью.

        Проверяет:
        - Статус код 422 (валидация Pydantic)
        """
        payload = {
            "aircraft_code": "TST",
            "model": "Test Aircraft",
            "range": 100,
        }

        response = await async_client.post(
            "/api/v2/aircrafts/add_aircraft", json=payload
        )

        assert response.status_code == 422


class TestUpdateAircraftRange:
    """
    Тесты для PATCH /aircrafts/{aircraft_code}/range
    """

    async def test_update_range_success(
        self,
        async_client: AsyncClient,
        test_aircrafts_v2: Aircrafts,
    ) -> None:
        """
        Тест успешного обновления дальности полета.

        Проверяет:
        - Статус код 200
        - Обновленное значение range
        """
        payload = {"range": 12000}

        response = await async_client.patch(
            f"/api/v2/aircrafts/{test_aircrafts_v2.aircraft_code}/range",
            json=payload,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["aircraft_code"] == "773"
        assert data["range"] == 12000
        assert data["model"] == "Boeing 777-300"

    async def test_update_range_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест обновления дальности для несуществующего самолета.

        Проверяет:
        - Статус код 404
        """
        payload = {"range": 5000}

        response = await async_client.patch(
            "/api/v2/aircrafts/XXX/range", json=payload
        )

        assert response.status_code == 404


class TestDeleteAircraft:
    """
    Тесты для DELETE /aircrafts/{aircraft_code}
    """

    async def test_delete_aircraft_success(
        self,
        async_client: AsyncClient,
        test_aircrafts_v2: Aircrafts,
    ) -> None:
        """
        Тест успешного удаления самолета.

        Проверяет:
        - Статус код 200
        - Сообщение об успешном удалении
        """
        response = await async_client.delete(
            f"/api/v2/aircrafts/{test_aircrafts_v2.aircraft_code}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "773" in data["message"]

    async def test_delete_aircraft_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест удаления несуществующего самолета.

        Проверяет:
        - Статус код 404
        """
        response = await async_client.delete("/api/v2/aircrafts/XXX")

        assert response.status_code == 404
