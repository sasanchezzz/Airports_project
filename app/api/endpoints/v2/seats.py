from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db_connection import get_db
from app.models.models import Seats
from app.schemas.seats import QPSeats, SeatsResponse


v2_seats_router = APIRouter(
    prefix="/seats",
    tags=["v2/seats"],
)


@v2_seats_router.get(
    "/",
    response_model=Page[SeatsResponse],
    summary="Get information about seat",
    response_description="Seat information",
)
async def get_seats(
    query: QPSeats = Depends(),
    session: AsyncSession = Depends(get_db),
    pagination_params: Params = Depends(),
) -> Page[SeatsResponse]:
    """
    Получение информации о доступных местах в самолете

    Тело запроса:
    - **aircraft_code**: уникальный код самолета
    - **fare_conditions**: категория места

    Параметры ответа:
    - **aircraft_code**: уникальный код самолета
    - **seat_no**: номер места в самолете
    - **fare_conditions**: категория места
    """

    query_conditions = query.compose_conditions(Seats)

    stmt = select(Seats).where(*query_conditions)

    get_seats_result: Page[SeatsResponse] = await paginate(
        session,
        stmt,
        pagination_params,
    )
    return get_seats_result
