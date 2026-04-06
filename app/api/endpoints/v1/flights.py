from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db_connection import get_db
from app.models.models import Aircrafts, Airports, Flights
from app.schemas.flights import (
    FlightsRequestJoin,
    FlightsResponse,
    FlightsResponseItem,
    QPFlights,
)


v1_flights_router = APIRouter(
    prefix="/flights",
    tags=["v1/flights"],
)


@v1_flights_router.get(
    "/",
    response_model=Page[FlightsResponse],
    summary="Get paginated information about flights",
    response_description="Flight information",
)
async def get_flights(
    query: QPFlights = Depends(),
    session: AsyncSession = Depends(get_db),
    pagination_params: Params = Depends(),
) -> Page[FlightsResponse]:
    """
    Получение информации о полете(ах) по нескольким параметрам, с пагинируемым ответом

    Параметры запроса:
    - **flight_no**: номер полета
    - **scheduled_departure**: запланированные дата и время отправления
    - **scheduled_arrival**: запланированные дата и время прибытия
    - **departure_airport**: аэропорт отправления
    - **arrival_airport**: аэропорт прибытия
    - **status**: статус полета
    - **aircraft_code**: код самолета
    - **actual_departure**: действительные дата и время отправления
    - **actual_arrival**: действительные дата и время прибытия

    Параметры ответа:
    - **flight_id**: id полета
    - **flight_no**: номер полета
    - **scheduled_departure**: запланированные дата и время отправления
    - **scheduled_arrival**: запланированные дата и время прибытия
    - **departure_airport**: аэропорт отправления
    - **arrival_airport**: аэропорт прибытия
    - **status**: статус полета
    - **aircraft_code**: код самолета
    - **actual_departure**: действительные дата и время отправления
    - **actual_arrival**: действительные дата и время прибытия
    """

    query_conditions = query.compose_conditions(Flights)

    stmt = (
        select(Flights)
        .where(*query_conditions)
        .order_by(Flights.flight_id)
    )

    get_flights_result: Page[FlightsResponse] = await paginate(
        session,
        stmt,
        pagination_params,
    )
    return get_flights_result


@v1_flights_router.get(
    "/city_flights",
    response_model=Page[FlightsResponseItem],
    summary="Get information about aircrafts for flights",
    response_description="Flight and aircraft info",
)
async def get_city_flights(
    query: FlightsRequestJoin = Depends(),
    session: AsyncSession = Depends(get_db),
    pagination_params: Params = Depends(),
) -> Page[FlightsResponseItem]:
    """
    Получение информации о полете и самолете по нескольким параметрам, с пагинируемым ответом

    Параметры запроса:
    - **flight_no**: номер полета
    - **departure_city**: город отправления
    - **arrival_city**: город прибытия
    - **status**: статус полета
    - **range**: дальность полета самолета

    Параметры ответа:
    - **flight_no**: номер полета
    - **airport_code**: уникальный код аэропорта
    - **range**: дальность полета самолета
    - **model**: модель самолета
    - **departure_airport**: аэропорт отправления
    - **departure_city**: город отправления
    - **arrival_airports**: аэропорт прибытия
    - **arrival_city**: город прибытия
    - **status**: статус полета
    """

    DeparureAirport = aliased(Airports)
    ArrivalAirport = aliased(Airports)
    AircraftsRange = aliased(Aircrafts)

    conditions = []
    if query.flight_no:
        conditions.append(Flights.flight_no == query.flight_no)
    if query.departure_city:
        conditions.append(
            DeparureAirport.city == query.departure_city
        )
    if query.arrival_city:
        conditions.append(ArrivalAirport.city == query.arrival_city)
    if query.status:
        conditions.append(Flights.status == query.status)
    if query.range:
        conditions.append(AircraftsRange.range == query.range)

    stmt = (
        select(
            Flights.flight_no,
            Flights.aircraft_code,
            Flights.departure_airport,
            DeparureAirport.city.label("departure_city"),
            Flights.arrival_airport,
            ArrivalAirport.city.label("arrival_city"),
            Flights.status,
            Aircrafts.range,
            Aircrafts.model,
        )
        .join(Aircrafts)
        .join(DeparureAirport, Flights.departure_airport_rel)
        .join(ArrivalAirport, Flights.arrival_airport_rel)
        .where(*conditions)
    )

    query_result: Page[FlightsResponseItem] = await paginate(
        session, stmt, pagination_params
    )
    return query_result
