from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate

from app.db_connection import get_db
from app.models.models import Airports
from app.schemas.airports import AirportResponse, QPAirports


airports_router = APIRouter(
    prefix="/airports",
    tags=["v1/airports"],
)


@airports_router.get("/", response_model=Page[AirportResponse])
async def get_airports(
    query_params: QPAirports = Depends(),
    session: AsyncSession = Depends(get_db),
    pagination_params: Params = Depends(),
) -> Page[AirportResponse]:
    query_conditions = query_params.compose_conditions(Airports)

    stmt = select(Airports).where(*query_conditions)

    get_airports_result: Page[
        AirportResponse
        ] = await paginate(
            session,
            stmt,
            pagination_params,
        )
    return get_airports_result
