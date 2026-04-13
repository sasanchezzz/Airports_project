from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import Aircrafts, Seats


@pytest_asyncio.fixture
async def test_seats_v2(session: AsyncSession) -> list[Seats]:
    """
    Создание тестовых данных для таблицы Seats (v2)
    """
    aircraft = Aircrafts(
        aircraft_code="773", model="Boeing 777-300", range=11100
    )
    session.add(aircraft)
    await session.commit()

    seats = [
        Seats(
            aircraft_code="773",
            seat_no="1A",
            fare_conditions="Business",
        ),
        Seats(
            aircraft_code="773",
            seat_no="2B",
            fare_conditions="Economy",
        ),
        Seats(
            aircraft_code="773",
            seat_no="3C",
            fare_conditions="Economy",
        ),
    ]

    session.add_all(seats)
    await session.commit()
    return seats


class TestGetSeats:
    """
    Тесты для GET /seats/
    """

    async def test_get_seats_empty(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест получения пустого списка мест.

        Проверяет:
        - Статус код 200
        - Пустой список items
        - Наличие пагинации
        """
        response = await async_client.get("/api/v2/seats/")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 0

    async def test_get_seats_with_data(
        self,
        async_client: AsyncClient,
        test_seats_v2: list[Seats],
    ) -> None:
        """
        Тест получения списка мест с данными.

        Проверяет:
        - Статус код 200
        - Наличие элементов в ответе
        - Корректность полей
        """
        response = await async_client.get("/api/v2/seats/")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 3
        assert data["total"] == 3

    async def test_get_seats_filter_by_aircraft(
        self,
        async_client: AsyncClient,
        test_seats_v2: list[Seats],
    ) -> None:
        """
        Тест фильтрации мест по коду самолета.

        Проверяет:
        - Статус код 200
        - Фильтрация по aircraft_code возвращает匹配的 результат
        """
        response = await async_client.get(
            "/api/v2/seats/", params={"aircraft_code": "773"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 3
        assert all(
            item["aircraft_code"] == "773" for item in data["items"]
        )

    async def test_get_seats_filter_by_fare(
        self,
        async_client: AsyncClient,
        test_seats_v2: list[Seats],
    ) -> None:
        """
        Тест фильтрации мест по категории.

        Проверяет:
        - Статус код 200
        - Фильтрация по fare_conditions возвращает匹配的 результат
        """
        response = await async_client.get(
            "/api/v2/seats/", params={"fare_conditions": "Business"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["fare_conditions"] == "Business"

    async def test_get_seats_pagination(
        self,
        async_client: AsyncClient,
        test_seats_v2: list[Seats],
    ) -> None:
        """
        Тест пагинации при получении списка мест.

        Проверяет:
        - Статус код 200
        - Параметр size влияет на количество элементов на странице
        """
        response = await async_client.get(
            "/api/v2/seats/", params={"size": 2, "page": 1}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        assert data["total"] == 3
