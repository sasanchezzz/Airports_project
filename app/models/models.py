from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from app.models.base import Base


class Aircrafts(Base):

    __tablename__ = "aircrafts"

    aircraft_code: Mapped[str] = mapped_column(
        String(3),
        primary_key=True,
        nullable=False,
    )
    model: Mapped[str]
    range: Mapped[int]

    flights: Mapped[list["Flights"]] = relationship(
        "Flights",
        back_populates="aircraft",
    )
    seats: Mapped[list["Seats"]] = relationship(
        "Seats",
        back_populates="aircraft",
    )


class Airports(Base):

    __tablename__ = "airports"

    airport_code: Mapped[str] = mapped_column(
        String(3),
        primary_key=True,
    )
    airport_name: Mapped[str]
    city: Mapped[str]
    longitude: Mapped[float]
    latitude: Mapped[float]
    timezone: Mapped[str]

    departure_airport: Mapped[list["Flights"]] = relationship(
        "Flights",
        foreign_keys="Flights.departure_airport",
        back_populates="departure_airport_rel",
    )
    arrival_airport: Mapped[list["Flights"]] = relationship(
        "Flights",
        foreign_keys="Flights.arrival_airport",
        back_populates="arrival_airport_rel",
    )


class Bookings(Base):

    __tablename__ = "bookings"

    book_ref: Mapped[str] = mapped_column(
        String(6),
        primary_key=True,
        nullable=False,
    )
    book_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    tickets: Mapped[list["Tickets"]] = relationship(
        "Tickets",
        back_populates="booking",
    )


class Seats(Base):

    __tablename__ = "seats"

    aircraft_code: Mapped[str] = mapped_column(
        String(3),
        ForeignKey("bookings.aircrafts.aircraft_code"),
        primary_key=True,
        nullable=False,
    )
    seat_no: Mapped[str] = mapped_column(
        String(4),
        primary_key=True,
        nullable=False,
    )
    fare_conditions: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    aircraft: Mapped["Aircrafts"] = relationship(
        "Aircrafts",
        back_populates="seats",
    )


class Flights(Base):

    __tablename__ = "flights"

    flight_id: Mapped[int] = mapped_column(
        nullable=False,
        primary_key=True,
    )
    flight_no: Mapped[str] = mapped_column(
        String(6),
        nullable=False,
    )
    scheduled_departure: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    scheduled_arrival: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    departure_airport: Mapped[str] = mapped_column(
        String(3),
        ForeignKey("bookings.airports.airport_code"),
        nullable=False,
    )
    arrival_airport: Mapped[str] = mapped_column(
        String(3),
        ForeignKey("bookings.airports.airport_code"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    aircraft_code: Mapped[str] = mapped_column(
        String(3),
        ForeignKey("bookings.aircrafts.aircraft_code"),
        nullable=False,
    )
    actual_departure: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )
    actual_arrival: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    aircraft: Mapped["Aircrafts"] = relationship(
        "Aircrafts",
        back_populates="flights",
    )
    departure_airport_rel: Mapped["Airports"] = relationship(
        "Airports",
        # foreign_keys=[Airports.departure_airport],
        primaryjoin="Airports.airport_code == Flights.departure_airport",
        back_populates="departure_airport",
    )
    arrival_airport_rel: Mapped["Airports"] = relationship(
        "Airports",
        # foreign_keys=[Airports.arrival_airport],
        primaryjoin="Airports.airport_code == Flights.arrival_airport",
        back_populates="arrival_airport",
    )
    ticket_flights: Mapped[list["TicketFlights"]] = relationship(
        "TicketFlights",
        back_populates="flight",
    )


class Tickets(Base):

    __tablename__ = "tickets"

    ticket_no: Mapped[str] = mapped_column(
        String(13),
        primary_key=True,
        nullable=False,
    )
    book_ref: Mapped[str] = mapped_column(
        String(6),
        ForeignKey("bookings.bookings.book_ref"),
        nullable=False,
    )
    passenger_id: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    passenger_name: Mapped[str] = mapped_column(nullable=False,)
    contact_data: Mapped[dict[str, str]] = mapped_column(
        JSONB,
        default=dict,
    )

    booking: Mapped["Bookings"] = relationship(
        "Bookings",
        back_populates="tickets",
    )
    ticket_flights: Mapped[list["TicketFlights"]] = relationship(
        "TicketFlights",
        back_populates="ticket",
    )


class TicketFlights(Base):

    __tablename__ = "ticket_flights"

    ticket_no: Mapped[str] = mapped_column(
        String(13),
        ForeignKey("bookings.tickets.ticket_no"),
        primary_key=True,
        nullable=False,
    )
    flight_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.flights.flight_id"),
        primary_key=True,
        nullable=False,
    )
    fare_conditions: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    flight: Mapped["Flights"] = relationship(
        "Flights",
        back_populates="ticket_flights",
    )
    ticket: Mapped["Tickets"] = relationship(
        "Tickets",
        back_populates="ticket_flights",
    )
    boarding_passes: Mapped[list["BoardingPasses"]] = relationship(
        "BoardingPasses",
        foreign_keys="BoardingPasses.ticket_no",
        back_populates="ticket_flight",
    )


class BoardingPasses(Base):

    __tablename__ = "boarding_passes"

    ticket_no: Mapped[str] = mapped_column(
        String(13),
        ForeignKey("bookings.ticket_flights.ticket_no"),
        primary_key=True,
        nullable=False,
    )
    flight_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bookings.ticket_flights.flight_id"),
        primary_key=True,
        nullable=False,
    )
    boarding_no: Mapped[int] = mapped_column(Integer, nullable=False)
    seat_no: Mapped[str] = mapped_column(
        String(4),
        nullable=False,
    )

    ticket_flight: Mapped["TicketFlights"] = relationship(
        "TicketFlights",
        foreign_keys="BoardingPasses.ticket_no",
        back_populates="boarding_passes",
    )
