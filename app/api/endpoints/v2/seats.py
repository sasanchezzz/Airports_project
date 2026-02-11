from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db_connection import get_db
from app.models.models import Seats
from app.schemas.seats import QPSeats, SeatsResponse


seats_router = APIRouter(
    prefix="/seats",
    tags=["v2/seats"],
)

@seats_router.get("/", response_model=Page[SeatsResponse])
async def get_airports(
    query: QPSeats = Depends(),
    session: AsyncSession = Depends(get_db),
    pagination_params: Params = Depends(),
) -> Page[SeatsResponse]:
    query_conditions = query.compose_conditions(Seats)

    stmt = select(Seats).where(*query_conditions)

    get_airports_result: Page[
        SeatsResponse
    ] = await paginate(
        session,
        stmt,
        pagination_params,
        )
    return get_airports_result

    # if result_get_seat_info is None:
    #     raise HTTPException(
    #             status_code=404,
    #             detail=f"Seat with number - {seat_no} not found"
    #         )
    # return get_seats_result
