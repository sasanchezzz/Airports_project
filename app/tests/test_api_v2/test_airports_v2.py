from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import Airports


@pytest_asyncio.fixture
async def test_airports_v2(session: AsyncSession) -> list[Airports]:
    """
    Создание тестовых данных для таблицы Airports (v2)
    """
    airports = [
        Airports(
            airport_code="SVO",
            airport_name="Шереметьево",
            city="Москва",
            longitude=37.4146,
            latitude=55.9726,
            timezone="Europe/Moscow",
        ),
        Airports(
            airport_code="LED",
            airport_name="Пулково",
            city="Санкт-Петербург",
            longitude=30.2625,
            latitude=59.8003,
            timezone="Europe/Moscow",
        ),
    ]

    session.add_all(airports)
    await session.commit()
    return airports


class TestUpsertAirports:
    """
    Тесты для POST /airports/upsert
    """

    async def test_upsert_airports_create(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест создания новых аэропортов через upsert.

        Проверяет:
        - Статус код 200
        - Сообщение об успехе
        - Список созданных аэропортов
        """
        payload = [
            {
                "airport_code": "KZN",
                "airport_name": "Казань",
                "city": "Казань",
                "longitude": 49.1028,
                "latitude": 55.6062,
                "timezone": "Europe/Moscow",
            }
        ]

        response = await async_client.post(
            "/api/v2/airports/upsert", json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert len(data["airports"]) == 1
        assert data["airports"][0]["airport_code"] == "KZN"
        assert data["airports"][0]["city"] == "Казань"

    async def test_upsert_airports_update(
        self,
        async_client: AsyncClient,
        test_airports_v2: list[Airports],
    ) -> None:
        """
        Тест обновления существующих аэропортов через upsert.

        Проверяет:
        - Статус код 200
        - Обновленные данные
        """
        payload = [
            {
                "airport_code": "SVO",
                "airport_name": "Шереметьево Обновлённый",
                "city": "Москва",
                "longitude": 37.4146,
                "latitude": 55.9726,
                "timezone": "Europe/Moscow",
            }
        ]

        response = await async_client.post(
            "/api/v2/airports/upsert", json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["airports"]) == 1
        assert data["airports"][0]["airport_name"] == "Шереметьево Обновлённый"

    async def test_upsert_airports_multiple(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест upsert нескольких аэропортов одновременно.

        Проверяет:
        - Статус код 200
        - Все аэропорты созданы
        """
        payload = [
            {
                "airport_code": "KZN",
                "airport_name": "Казань",
                "city": "Казань",
                "longitude": 49.1028,
                "latitude": 55.6062,
                "timezone": "Europe/Moscow",
            },
            {
                "airport_code": "SVX",
                "airport_name": "Кольцово",
                "city": "Екатеринбург",
                "longitude": 60.8027,
                "latitude": 56.7431,
                "timezone": "Asia/Yekaterinburg",
            },
        ]

        response = await async_client.post(
            "/api/v2/airports/upsert", json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["airports"]) == 2


class TestDeleteAirport:
    """
    Тесты для DELETE /airports/{airport_code}
    """

    async def test_delete_airport_success(
        self,
        async_client: AsyncClient,
        test_airports_v2: list[Airports],
    ) -> None:
        """
        Тест успешного удаления аэропорта.

        Проверяет:
        - Статус код 200
        - Сообщение об успешном удалении
        """
        response = await async_client.delete("/api/v2/airports/SVO")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "SVO" in data["message"]

    async def test_delete_airport_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест удаления несуществующего аэропорта.

        Проверяет:
        - Статус код 404
        """
        response = await async_client.delete("/api/v2/airports/XXX")

        assert response.status_code == 404
