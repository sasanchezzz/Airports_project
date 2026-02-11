from datetime import datetime

from pydantic import BaseModel

from app.schemas.mixin import ConditionsMixin


class QPFlights(ConditionsMixin):
    """
    Параметры запроса для таблицы flights

    Параметры опциональны, используются только переданные значения
    Attributes:
        flight_no: str | None - Номер рейса

        scheduled_departure: datetime | None - Запланированные дата и время отправления, пример: 2011-12-12 10:20:00+00

        scheduled_arrival: datetime | None - Запланированные дата и время прибытия, пример: 2012-01-01 15:30:00+00

        departure_airport: str | None - Аэропорт отправления, пример: "SVO"

        arrival_airport: str | None - Аэропорт прибытия, пример: "SVO"

        status: str | None - Статус полета, пример: "On Time"

        aircraft_code: str | None - Код самолета, пример: "321"

        actual_departure: datetime | None - Действительные дата и время отправления, пример: 2011-12-12 10:20:00+00

        actual_arrival: datetime | None - Действительные дата и время прибытия, пример: 2012-01-01 15:30:00+00
    """
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
    """
    Модель ответа для таблицы flights
    Attributes:
        flights_id: int - Уникальный ID для полета

        flight_no: str - Номер рейса

        scheduled_departure: datetime - Запланированные дата и время отправления, пример: 2011-12-12 10:20:00+00

        scheduled_arrival: datetime - Запланированные дата и время прибытия, пример: 2012-01-01 15:30:00+00

        departure_airport: str - Аэропорт отправления, пример: "SVO"

        arrival_airport: str - Аэропорт прибытия, пример: "SVO"

        status: str - Статус полета, пример: "On Time"

        aircraft_code: str - Код самолета, пример: "321"

        actual_departure: datetime - Действительные дата и время отправления, пример: 2011-12-12 10:20:00+00

        actual_arrival: datetime - Действительные дата и время прибытия, пример: 2012-01-01 15:30:00+00
    """
    flight_id: int
    flight_no: str
    scheduled_departure: datetime
    scheduled_arrival: datetime
    departure_airport: str
    arrival_airport: str
    status: str
    aircraft_code: str
    actual_departure: datetime
    actual_arrival: datetime


class FlightsRequestJoin(BaseModel):
    """
    Модель для join-запроса с таблицами aircrafts и airports

    Параметры опциональны, используются только переданные значения
    Attributes:
        flight_no: str | None - Номер рейса

        departure_city: str | None - Город отбытия

        arrival_city: str | None - Город прибытия

        status: str | None - Статус полета

        range: int | None - Максимальная дальность полета самолета в километрах
    """
    flight_no: str | None = None
    departure_city: str | None = None
    arrival_city: str | None = None
    status: str | None = None
    range: int | None = None


class FlightsResponseItem(ConditionsMixin):
    """
    Модель ответа для join-запроса с таблицами aircrafts и airports
    Attributes:
        flight_no: str - Номер рейса

        aircraft_code: str - Код самолета, пример: "321"

        departure_airport: str - Аэропорт отправления, пример: "SVO"

        departure_city: str - Город отбытия

        arrival_airport: str - Аэропорт прибытия, пример: "SVO"

        arrival_city: str - Город прибытия

        status: str - Статус полета

        range: int - Максимальная дальность полета самолета в километрах

        model: str - Модель самолета
    """
    flight_no: str
    aircraft_code: str
    departure_airport: str
    departure_city: str
    arrival_airport: str
    arrival_city: str
    status: str
    range: int
    model: str
