from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import aliased

from app.db_connection import get_db
from app.models.models import Airports, Flights, Seats, TicketFlights
from app.schemas.flights import (
    FlightsAnalyticsRequest,
    PeriodDate,
    TopRouteItem,
    TopRouteResponse,
)


v2_flights_router = APIRouter(prefix="/flights", tags=["v2/flights"])


@v2_flights_router.get("/analytics", response_model=TopRouteResponse)
async def get_flights_anlytics(
    query: FlightsAnalyticsRequest = Depends(),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
) -> TopRouteResponse:
    DepartureAirport = aliased(Airports)
    ArrivalAirport = aliased(Airports)

    seats_subquery = (
        select(Seats.aircraft_code, func.count().label("total_seats"))
        .group_by(Seats.aircraft_code)
        .subquery()
    )

    sold_tickets_subquery = (
        select(
            TicketFlights.flight_id,
            func.count().label("sold_tickets"),
            func.sum(TicketFlights.amount).label("flights_revenue"),
        )
        .group_by(TicketFlights.flight_id)
        .subquery()
    )

    passengers_expr = func.coalesce(
        func.sum(sold_tickets_subquery.c.sold_tickets), 0
    ).label("passengers")

    avg_load_factor_expr = func.avg(
        func.coalesce(sold_tickets_subquery.c.sold_tickets, 0)
        * 100
        / func.coalesce(seats_subquery.c.total_seats, 1)
    ).label("avg_load_factor")

    revenue_expr = func.coalesce(
        func.sum(sold_tickets_subquery.c.flights_revenue),
        0,
    ).label("revenue")
    stmt = (
        (
            select(
                func.concat(
                    Flights.departure_airport,
                    literal(" - "),
                    Flights.arrival_airport,
                ).label("route"),
                DepartureAirport.city.label("depart_city"),
                ArrivalAirport.city.label("arrival_city"),
                func.count(Flights.flight_id.distinct()).label(
                    "flights_count"
                ),
                passengers_expr,
                avg_load_factor_expr,
                revenue_expr,
            )
            .select_from(Flights)
            .join(DepartureAirport, Flights.departure_airport_rel)
            .join(ArrivalAirport, Flights.arrival_airport_rel)
            .outerjoin(
                sold_tickets_subquery,
                sold_tickets_subquery.c.flight_id
                == Flights.flight_id,
            )
            .outerjoin(
                seats_subquery,
                seats_subquery.c.aircraft_code
                == Flights.aircraft_code,
            )
            .where(
                (Flights.scheduled_departure >= query.date_from)
                & (Flights.scheduled_departure <= query.date_to)
                & (Flights.status != "Cancelled")
            )
        )
        .group_by(
            Flights.departure_airport,
            Flights.arrival_airport,
            DepartureAirport.city,
            ArrivalAirport.city,
        )
        .order_by(desc("revenue"))
    )

    paginated_stmt = stmt.offset((page - 1) * size).limit(size)

    result = await session.execute(paginated_stmt)
    rows = result.all()

    top_routes = [
        TopRouteItem(
            route=r.route,
            departure_city=r.depart_city,
            arrival_city=r.arrival_city,
            flights_count=r.flights_count,
            passengers=int(r.passengers) if r.passengers else 0,
            avg_load_factor=float(r.avg_load_factor)
            if r.avg_load_factor
            else 0.0,
            revenue=float(r.revenue) if r.revenue else 0.0,
        )
        for r in rows
    ]

    return TopRouteResponse(
        period=[
            PeriodDate(
                from_date=query.date_from, to_date=query.date_to
            )
        ],
        top_routes=top_routes,
    )
