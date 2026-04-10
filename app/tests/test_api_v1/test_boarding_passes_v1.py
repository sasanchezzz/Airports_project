from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import (
    Aircrafts,
    Airports,
    BoardingPasses,
    Bookings,
    Flights,
    TicketFlights,
    Tickets,
)


@pytest_asyncio.fixture
async def test_boarding_pass_setup(
    session: AsyncSession,
) -> dict[str, Any]:
    """
    Создание тестовых данных для boarding passes:
    Aircrafts -> Airports -> Bookings -> Flights -> Tickets -> TicketFlights -> BoardingPasses
    """
    from datetime import datetime, timezone

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

    booking = Bookings(book_ref="ABC123", total_amount=50000.00)
    session.add(booking)
    await session.commit()

    flight = Flights(
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
    )
    session.add(flight)
    await session.commit()

    ticket = Tickets(
        ticket_no="1234567890123",
        book_ref="ABC123",
        passenger_id="PASS001",
        passenger_name="IVAN IVANOV",
        contact_data={"phone": "+79001234567"},
    )
    session.add(ticket)
    await session.commit()

    ticket_flight = TicketFlights(
        ticket_no="1234567890123",
        flight_id=1,
        fare_conditions="Economy",
        amount=25000.00,
    )
    session.add(ticket_flight)
    await session.commit()

    boarding_pass = BoardingPasses(
        ticket_no="1234567890123",
        flight_id=1,
        boarding_no=1,
        seat_no="1A",
    )
    session.add(boarding_pass)
    await session.commit()

    return {
        "ticket_no": "1234567890123",
        "flight_id": 1,
        "boarding_no": 1,
        "seat_no": "1A",
    }


class TestGetBoardingPass:
    """
    Тесты для GET /boarding_passes/{ticket_no}
    """

    async def test_get_boarding_pass_success(
        self,
        async_client: AsyncClient,
        test_boarding_pass_setup: dict[str, Any],
    ) -> None:
        """
        Тест успешного получения информации о посадочном талоне.

        Проверяет:
        - Статус код 200
        - Корректность возвращаемых данных
        """
        ticket_no = test_boarding_pass_setup["ticket_no"]
        response = await async_client.get(
            f"/api/v1/boarding_passes/{ticket_no}"
        )

        assert response.status_code == 200
        data = response.json()

        assert (
            data["flight_id"] == test_boarding_pass_setup["flight_id"]
        )
        assert (
            data["boarding_no"]
            == test_boarding_pass_setup["boarding_no"]
        )
        assert data["seat_no"] == test_boarding_pass_setup["seat_no"]

    async def test_get_boarding_pass_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест получения информации о несуществующем посадочном талоне.

        Проверяет:
        - Статус код 404
        - Наличие сообщения об ошибке
        """
        response = await async_client.get(
            "/api/v1/boarding_passes/0000000000000"
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
