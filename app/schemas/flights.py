from datetime import datetime

from pydantic import BaseModel

from app.schemas.base import ConditionsMixin


class FlightsQP(ConditionsMixin):
    flight_no: str | None = None
    scheduled_departure: datetime | None = None
    scheduled_arrival: datetime | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    status: str | None = None
    aircraft_code: str | None = None
    actual_departure: datetime | None = None
    actual_arrival: datetime | None = None


class FlightsResponse(BaseModel):
    flight_id: int | None = None
    flight_no: str | None = None
    scheduled_departure: datetime | None = None
    scheduled_arrival: datetime | None = None
    departure_airport: str | None = None
    arrival_airport: str | None = None
    status: str | None = None
    aircraft_code: str | None = None
    actual_departure: datetime | None = None
    actual_arrival: datetime | None = None


class FlightsRequestJoin(BaseModel):
    flight_no: str | None = None
    departure_city: str | None = None
    arrival_city: str | None = None
    status: str | None = None
    range: int | None = None


class FlightsResponseItem(ConditionsMixin):
    flight_no: str | None = None
    aircraft_code: str | None = None
    departure_airport: str | None = None
    departure_city: str | None = None
    arrival_airport: str | None = None
    arrival_city: str | None = None
    status: str | None = None
    range: int | None = None
    model: str | None = None
