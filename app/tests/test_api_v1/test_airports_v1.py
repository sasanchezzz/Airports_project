from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import Airports


@pytest_asyncio.fixture
async def test_airports(session: AsyncSession) -> list[Airports]:
    """
    Создание тестовых данных для таблицы Airports
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


class TestGetAirports:
    """
    Тесты для GET /airports/
    """

    async def test_get_airports_empty(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест получения пустого списка аэропортов.

        Проверяет:
        - Статус код 200
        - Пустой список items
        - Наличие пагинации
        """
        response = await async_client.get("/api/v1/airports/")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["items"]) == 0

    async def test_get_airports_with_data(
        self,
        async_client: AsyncClient,
        test_airports: list[Airports],
    ) -> None:
        """
        Тест получения списка аэропортов с данными.

        Проверяет:
        - Статус код 200
        - Наличие элементов в ответе
        - Корректность полей каждого аэропорта
        """
        response = await async_client.get("/api/v1/airports/")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2
        assert data["total"] == 2

        svo = next(
            item
            for item in data["items"]
            if item["airport_code"] == "SVO"
        )
        assert svo["airport_name"] == "Шереметьево"
        assert svo["city"] == "Москва"
        assert svo["timezone"] == "Europe/Moscow"

    async def test_get_airports_filter_by_code(
        self,
        async_client: AsyncClient,
        test_airports: list[Airports],
    ) -> None:
        """
        Тест фильтрации аэропортов по коду.

        Проверяет:
        - Статус код 200
        - Фильтрация по airport_code возвращает только результат
        """
        response = await async_client.get(
            "/api/v1/airports/", params={"airport_code": "LED"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["airport_code"] == "LED"

    async def test_get_airports_filter_by_city(
        self,
        async_client: AsyncClient,
        test_airports: list[Airports],
    ) -> None:
        """
        Тест фильтрации аэропортов по городу.

        Проверяет:
        - Статус код 200
        - Фильтрация по city возвращает только匹配的 результат
        """
        response = await async_client.get(
            "/api/v1/airports/", params={"city": "Москва"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["city"] == "Москва"

    async def test_get_airports_pagination(
        self,
        async_client: AsyncClient,
        test_airports: list[Airports],
    ) -> None:
        """
        Тест пагинации при получении списка аэропортов.

        Проверяет:
        - Статус код 200
        - Параметр size влияет на количество элементов на странице
        - Параметр page переключает страницы
        """
        response = await async_client.get(
            "/api/v1/airports/", params={"size": 1, "page": 1}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["page"] == 1
        assert data["size"] == 1
        assert data["total"] == 2
