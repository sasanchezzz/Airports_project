from datetime import datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import (
    Aircrafts,
    Airports,
    Flights,
)


@pytest_asyncio.fixture
async def test_flights_setup(
    session: AsyncSession,
) -> list[Flights]:
    """
    Создание тестовых данных для таблицы Flights
    """
    aircraft = Aircrafts(
        aircraft_code="773", model="Boeing 777-300", range=11100
    )
    session.add(aircraft)

    airport_dep = Airports(
        airport_code="SVO",
        airport_name="Шереметьево",
        city="Москва",
        longitude=37.4146,
        latitude=55.9726,
        timezone="Europe/Moscow",
    )
    airport_arr = Airports(
        airport_code="LED",
        airport_name="Пулково",
        city="Санкт-Петербург",
        longitude=30.2625,
        latitude=59.8003,
        timezone="Europe/Moscow",
    )
    session.add_all([airport_dep, airport_arr])
    await session.commit()

    flights = [
        Flights(
            flight_id=1,
            flight_no="SU1234",
            scheduled_departure=datetime(
                2025, 6, 1, 10, 0, tzinfo=timezone.utc
            ),
            scheduled_arrival=datetime(
                2025, 6, 1, 12, 0, tzinfo=timezone.utc
            ),
            departure_airport="SVO",
            arrival_airport="LED",
            status="On Time",
            aircraft_code="773",
            actual_departure=datetime(
                2025, 6, 1, 10, 5, tzinfo=timezone.utc
            ),
            actual_arrival=datetime(
                2025, 6, 1, 12, 5, tzinfo=timezone.utc
            ),
        ),
        Flights(
            flight_id=2,
            flight_no="SU5678",
            scheduled_departure=datetime(
                2025, 6, 2, 14, 0, tzinfo=timezone.utc
            ),
            scheduled_arrival=datetime(
                2025, 6, 2, 16, 0, tzinfo=timezone.utc
            ),
            departure_airport="LED",
            arrival_airport="SVO",
            status="Delayed",
            aircraft_code="773",
            actual_departure=datetime(
                2025, 6, 2, 14, 30, tzinfo=timezone.utc
            ),
            actual_arrival=datetime(
                2025, 6, 2, 16, 30, tzinfo=timezone.utc
            ),
        ),
    ]

    session.add_all(flights)
    await session.commit()
    return flights


class TestGetFlights:
    """
    Тесты для GET /flights/
    """

    async def test_get_flights_empty(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест получения пустого списка рейсов.

        Проверяет:
        - Статус код 200
        - Пустой список items
        - Наличие пагинации
        """
        response = await async_client.get("/api/v1/flights/")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 0

    async def test_get_flights_with_data(
        self,
        async_client: AsyncClient,
        test_flights_setup: list[Flights],
    ) -> None:
        """
        Тест получения списка рейсов с данными.

        Проверяет:
        - Статус код 200
        - Наличие элементов в ответе
        - Корректность полей
        """
        response = await async_client.get("/api/v1/flights/")

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2
        assert data["total"] == 2

        flight_1 = next(
            item for item in data["items"] if item["flight_id"] == 1
        )
        assert flight_1["flight_no"] == "SU1234"
        assert flight_1["departure_airport"] == "SVO"
        assert flight_1["arrival_airport"] == "LED"
        assert flight_1["status"] == "On Time"
        assert flight_1["aircraft_code"] == "773"

    async def test_get_flights_filter_by_status(
        self,
        async_client: AsyncClient,
        test_flights_setup: list[Flights],
    ) -> None:
        """
        Тест фильтрации рейсов по статусу.

        Проверяет:
        - Статус код 200
        - Фильтрация по status возвращает только匹配的 результат
        """
        response = await async_client.get(
            "/api/v1/flights/", params={"status": "Delayed"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "Delayed"

    async def test_get_flights_filter_by_airport(
        self,
        async_client: AsyncClient,
        test_flights_setup: list[Flights],
    ) -> None:
        """
        Тест фильтрации рейсов по аэропорту отправления.

        Проверяет:
        - Статус код 200
        - Фильтрация по departure_airport возвращает только匹配的 результат
        """
        response = await async_client.get(
            "/api/v1/flights/", params={"departure_airport": "SVO"}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["departure_airport"] == "SVO"

    async def test_get_flights_pagination(
        self,
        async_client: AsyncClient,
        test_flights_setup: list[Flights],
    ) -> None:
        """
        Тест пагинации при получении списка рейсов.

        Проверяет:
        - Статус код 200
        - Параметр size влияет на количество элементов на странице
        """
        response = await async_client.get(
            "/api/v1/flights/", params={"size": 1, "page": 1}
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["page"] == 1
        assert data["size"] == 1
        assert data["total"] == 2


class TestGetCityFlights:
    """
    Тесты для GET /flights/city_flights
    """

    async def test_get_city_flights_empty(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест получения пустого списка рейсов с городами.

        Проверяет:
        - Статус код 200
        - Пустой список items
        """
        response = await async_client.get(
            "/api/v1/flights/city_flights"
        )

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert len(data["items"]) == 0

    async def test_get_city_flights_with_data(
        self,
        async_client: AsyncClient,
        test_flights_setup: list[Flights],
    ) -> None:
        """
        Тест получения списка рейсов с городами и данными о самолёте.

        Проверяет:
        - Статус код 200
        - Наличие элементов в ответе
        - Корректность полей, включая join-данные
        """
        response = await async_client.get(
            "/api/v1/flights/city_flights"
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 2

        flight_1 = next(
            item
            for item in data["items"]
            if item["flight_no"] == "SU1234"
        )
        assert flight_1["departure_airport"] == "SVO"
        assert flight_1["departure_city"] == "Москва"
        assert flight_1["arrival_airport"] == "LED"
        assert flight_1["arrival_city"] == "Санкт-Петербург"
        assert flight_1["status"] == "On Time"
        assert flight_1["model"] == "Boeing 777-300"
        assert flight_1["range"] == 11100

    async def test_get_city_flights_filter_by_city(
        self,
        async_client: AsyncClient,
        test_flights_setup: list[Flights],
    ) -> None:
        """
        Тест фильтрации рейсов по городу отправления.

        Проверяет:
        - Статус код 200
        - Фильтрация по departure_city возвращает только匹配的 результат
        """
        response = await async_client.get(
            "/api/v1/flights/city_flights",
            params={"departure_city": "Москва"},
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["departure_city"] == "Москва"

    async def test_get_city_flights_filter_by_status(
        self,
        async_client: AsyncClient,
        test_flights_setup: list[Flights],
    ) -> None:
        """
        Тест фильтрации рейсов по статусу в city_flights.

        Проверяет:
        - Статус код 200
        - Фильтрация по status возвращает только匹配的 результат
        """
        response = await async_client.get(
            "/api/v1/flights/city_flights",
            params={"status": "Delayed"},
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "Delayed"
