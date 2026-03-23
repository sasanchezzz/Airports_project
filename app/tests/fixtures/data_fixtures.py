from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import (
    Aircrafts,
    Airports,
    BoardingPasses,
    Bookings,
    Flights,
    Seats,
    TicketFlights,
    Tickets,
)


@pytest_asyncio.fixture
async def test_aircrafts(session: AsyncSession) -> list[Aircrafts]:
    """
    Создание тестовых данных для таблицы Aircrafts
    """
    aircrafts = [
        Aircrafts(
            aircraft_code="773", model="Boeing 777-300", range=11100
        ),
        Aircrafts(
            aircraft_code="763", model="Boeing 767-300", range=7900
        ),
        Aircrafts(
            aircraft_code="SU9",
            model="Sukhoi SuperJet-100",
            range=3000,
        ),
        Aircrafts(
            aircraft_code="320", model="Airbus A320-200", range=5700
        ),
        Aircrafts(
            aircraft_code="321", model="Airbus A321-200", range=5600
        ),
    ]

    for aircraft in aircrafts:
        session.add(aircraft)

    await session.commit()

    for aircraft in aircrafts:
        await session.refresh(aircraft)

    return aircrafts


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
            longitude=37.414589,
            latitude=55.972642,
            timezone="Europe/Moscow",
        ),
        Airports(
            airport_code="LED",
            airport_name="Пулково",
            city="Санкт-Петербург",
            longitude=30.262503,
            latitude=59.800292,
            timezone="Europe/Moscow",
        ),
        Airports(
            airport_code="KZN",
            airport_name="Казань",
            city="Казань",
            longitude=49.278728,
            latitude=55.606186,
            timezone="Europe/Moscow",
        ),
        Airports(
            airport_code="AER",
            airport_name="Сочи",
            city="Сочи",
            longitude=39.956589,
            latitude=43.449928,
            timezone="Europe/Moscow",
        ),
        Airports(
            airport_code="IKT",
            airport_name="Иркутск",
            city="Иркутск",
            longitude=104.388975,
            latitude=52.268028,
            timezone="Asia/Irkutsk",
        ),
        Airports(
            airport_code="VVO",
            airport_name="Владивосток",
            city="Владивосток",
            longitude=132.148017,
            latitude=43.398953,
            timezone="Asia/Vladivostok",
        ),
    ]

    for airport in airports:
        session.add(airport)

    await session.commit()

    for airport in airports:
        await session.refresh(airport)

    return airports


@pytest_asyncio.fixture
async def test_seats(
    session: AsyncSession, test_aircrafts: list[Aircrafts]
) -> list[Seats]:
    """
    Создание тестовых данных для таблицы Seats
    """
    seats = []

    aircraft_773 = next(
        a for a in test_aircrafts if a.aircraft_code == "773"
    )
    for row in range(1, 6):
        for letter in ["A", "B", "C", "D", "E", "F"]:
            fare = "Economy" if row > 3 else "Business"
            seats.append(
                Seats(
                    aircraft_code=aircraft_773.aircraft_code,
                    seat_no=f"{row}{letter}",
                    fare_conditions=fare,
                )
            )

    aircraft_su9 = next(
        a for a in test_aircrafts if a.aircraft_code == "SU9"
    )
    for row in range(1, 4):
        for letter in ["A", "B", "C", "D"]:
            fare = "Economy"
            seats.append(
                Seats(
                    aircraft_code=aircraft_su9.aircraft_code,
                    seat_no=f"{row}{letter}",
                    fare_conditions=fare,
                )
            )

    for seat in seats:
        session.add(seat)

    await session.commit()

    for seat in seats:
        await session.refresh(seat)

    return seats


@pytest_asyncio.fixture
async def test_bookings(session: AsyncSession) -> list[Bookings]:
    """
    Создание тестовых данных для таблицы Bookings
    """
    bookings = [
        Bookings(
            book_ref="ABC123",
            book_date=datetime.now(timezone.utc) - timedelta(days=5),
            total_amount=50000.00,
        ),
        Bookings(
            book_ref="DEF456",
            book_date=datetime.now(timezone.utc) - timedelta(days=3),
            total_amount=35000.00,
        ),
        Bookings(
            book_ref="GHI789",
            book_date=datetime.now(timezone.utc) - timedelta(days=1),
            total_amount=75000.00,
        ),
    ]

    for booking in bookings:
        session.add(booking)

    await session.commit()

    for booking in bookings:
        await session.refresh(booking)

    return bookings


@pytest_asyncio.fixture
async def test_flights(
    session: AsyncSession,
) -> list[Flights]:
    """
    Создание тестовых данных для таблицы Flights
    """
    now = datetime.now(timezone.utc)

    flights = [
        Flights(
            flight_id=1,
            flight_no="PG0504",
            scheduled_departure=now + timedelta(days=1),
            scheduled_arrival=now
            + timedelta(days=1, hours=1, minutes=30),
            departure_airport="SVO",
            arrival_airport="LED",
            status="Scheduled",
            aircraft_code="SU9",
            actual_departure=None,
            actual_arrival=None,
        ),
        Flights(
            flight_id=2,
            flight_no="SU1021",
            scheduled_departure=now + timedelta(days=2),
            scheduled_arrival=now + timedelta(days=2, hours=8),
            departure_airport="SVO",
            arrival_airport="IKT",
            status="Scheduled",
            aircraft_code="773",
            actual_departure=None,
            actual_arrival=None,
        ),
        Flights(
            flight_id=3,
            flight_no="SU1037",
            scheduled_departure=now - timedelta(hours=2),
            scheduled_arrival=now - timedelta(hours=1),
            departure_airport="LED",
            arrival_airport="SVO",
            status="Departed",
            aircraft_code="SU9",
            actual_departure=now - timedelta(hours=2, minutes=5),
            actual_arrival=None,
        ),
        Flights(
            flight_id=4,
            flight_no="SU1043",
            scheduled_departure=now - timedelta(days=1),
            scheduled_arrival=now - timedelta(days=1, hours=8),
            departure_airport="SVO",
            arrival_airport="VVO",
            status="Arrived",
            aircraft_code="773",
            actual_departure=now - timedelta(days=1, hours=2),
            actual_arrival=now
            - timedelta(days=1, hours=8, minutes=10),
        ),
    ]

    for flight in flights:
        session.add(flight)

    await session.commit()

    for flight in flights:
        await session.refresh(flight)

    return flights


@pytest_asyncio.fixture
async def test_tickets(
    session: AsyncSession,
) -> list[Tickets]:
    """
    Создание тестовых данных для таблицы Tickets
    """
    tickets = [
        Tickets(
            ticket_no="1234567890123",
            book_ref="ABC123",
            passenger_id="1234 567890",
            passenger_name="IVAN PETROV",
            contact_data={
                "phone": "+71234567890",
                "email": "ivan@example.com",
            },
        ),
        Tickets(
            ticket_no="1234567890124",
            book_ref="ABC123",
            passenger_id="1234 567891",
            passenger_name="MARIA IVANOVA",
            contact_data={"phone": "+79876543210"},
        ),
        Tickets(
            ticket_no="1234567890125",
            book_ref="DEF456",
            passenger_id="1234 567892",
            passenger_name="PETR SIDOROV",
            contact_data={
                "phone": "+71112223344",
                "email": "petr@example.com",
            },
        ),
        Tickets(
            ticket_no="1234567890126",
            book_ref="GHI789",
            passenger_id="1234 567893",
            passenger_name="OLGA SMIRNOVA",
            contact_data={"email": "olga@example.com"},
        ),
        Tickets(
            ticket_no="1234567890127",
            book_ref="GHI789",
            passenger_id="1234 567894",
            passenger_name="MIKHAIL KUZNETSOV",
            contact_data={"phone": "+74445556677"},
        ),
    ]

    for ticket in tickets:
        session.add(ticket)

    await session.commit()

    for ticket in tickets:
        await session.refresh(ticket)

    return tickets


@pytest_asyncio.fixture
async def test_ticket_flights(
    session: AsyncSession,
) -> list[TicketFlights]:
    """
    Создание тестовых данных для таблицы TicketsFlights
    """
    ticket_flights = [
        TicketFlights(
            ticket_no="1234567890123",
            flight_id=1,
            fare_conditions="Economy",
            amount=5000.00,
        ),
        TicketFlights(
            ticket_no="1234567890124",
            flight_id=1,
            fare_conditions="Economy",
            amount=5000.00,
        ),
        TicketFlights(
            ticket_no="1234567890125",
            flight_id=2,
            fare_conditions="Business",
            amount=35000.00,
        ),
        TicketFlights(
            ticket_no="1234567890126",
            flight_id=3,
            fare_conditions="Economy",
            amount=7500.00,
        ),
        TicketFlights(
            ticket_no="1234567890127",
            flight_id=3,
            fare_conditions="Economy",
            amount=7500.00,
        ),
    ]

    for ticket_flight in ticket_flights:
        session.add(ticket_flight)

    await session.commit()

    for ticket_flight in ticket_flights:
        await session.refresh(ticket_flight)

    return ticket_flights


@pytest_asyncio.fixture
async def test_boarding_passes(
    session: AsyncSession,
) -> list[BoardingPasses]:
    """
    Создание тестовых данных для таблицы BoardingPasses
    """
    boarding_passes = [
        BoardingPasses(
            ticket_no="1234567890123",
            flight_id=1,
            boarding_no=1,
            seat_no="1A",
        ),
        BoardingPasses(
            ticket_no="1234567890124",
            flight_id=1,
            boarding_no=2,
            seat_no="1B",
        ),
        BoardingPasses(
            ticket_no="1234567890126",
            flight_id=3,
            boarding_no=5,
            seat_no="2C",
        ),
        BoardingPasses(
            ticket_no="1234567890127",
            flight_id=3,
            boarding_no=6,
            seat_no="2D",
        ),
    ]

    for boarding_pass in boarding_passes:
        session.add(boarding_pass)

    await session.commit()

    for boarding_pass in boarding_passes:
        await session.refresh(boarding_pass)

    return boarding_passes
