from datetime import date, datetime, timezone

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import (
    Aircrafts,
    Airports,
    Flights,
)


@pytest_asyncio.fixture
async def test_flights_v2_setup(
    session: AsyncSession,
) -> list[Flights]:
    """
    Создание тестовых данных для v2 flights analytics
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
            status="On Time",
            aircraft_code="773",
            actual_departure=datetime(
                2025, 6, 2, 14, 30, tzinfo=timezone.utc
            ),
            actual_arrival=datetime(
                2025, 6, 2, 16, 30, tzinfo=timezone.utc
            ),
        ),
        Flights(
            flight_id=3,
            flight_no="SU9999",
            scheduled_departure=datetime(
                2025, 6, 3, 8, 0, tzinfo=timezone.utc
            ),
            scheduled_arrival=datetime(
                2025, 6, 3, 10, 0, tzinfo=timezone.utc
            ),
            departure_airport="SVO",
            arrival_airport="LED",
            status="Cancelled",
            aircraft_code="773",
            actual_departure=datetime(
                2025, 6, 3, 8, 0, tzinfo=timezone.utc
            ),
            actual_arrival=datetime(
                2025, 6, 3, 10, 0, tzinfo=timezone.utc
            ),
        ),
    ]

    session.add_all(flights)
    await session.commit()
    return flights


class TestGetFlightsAnalytics:
    """
    Тесты для GET /flights/analytics
    """

    async def test_analytics_empty(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест аналитики при отсутствии данных.

        Проверяет:
        - Статус код 200
        - Пустой список top_routes
        - Наличие period
        """
        response = await async_client.get(
            "/api/v2/flights/analytics",
            params={
                "date_from": "2025-01-01",
                "date_to": "2025-12-31",
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert "period" in data
        assert "top_routes" in data
        assert len(data["top_routes"]) == 0

    async def test_analytics_with_data(
        self,
        async_client: AsyncClient,
        test_flights_v2_setup: list[Flights],
    ) -> None:
        """
        Тест аналитики с данными (исключая Cancelled).

        Проверяет:
        - Статус код 200
        - Наличие маршрутов в ответе
        - Cancelled рейсы не учитываются
        - Корректность полей
        """
        response = await async_client.get(
            "/api/v2/flights/analytics",
            params={
                "date_from": "2025-06-01",
                "date_to": "2025-06-30",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Cancelled рейс (flight_id=3) не должен учитываться
        # Ожидаем 2 маршрута: SVO-LED и LED-SVO
        assert len(data["top_routes"]) == 2

        # Проверяем что маршрут SVO - LED есть
        svo_led = next(
            (r for r in data["top_routes"] if r["route"] == "SVO - LED"),
            None,
        )
        assert svo_led is not None
        assert svo_led["departure_city"] == "Москва"
        assert svo_led["arrival_city"] == "Санкт-Петербург"
        assert svo_led["flights_count"] == 1

    async def test_analytics_pagination(
        self,
        async_client: AsyncClient,
        test_flights_v2_setup: list[Flights],
    ) -> None:
        """
        Тест пагинации в аналитике.

        Проверяет:
        - Статус код 200
        - Параметр size ограничивает количество результатов
        """
        response = await async_client.get(
            "/api/v2/flights/analytics",
            params={
                "date_from": "2025-06-01",
                "date_to": "2025-06-30",
                "page": 1,
                "size": 1,
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert len(data["top_routes"]) == 1
