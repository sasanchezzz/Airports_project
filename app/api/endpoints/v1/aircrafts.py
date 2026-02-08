from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db_connection import get_db
from app.models.models import Aircrafts
from app.schemas.aircrafts import AircraftResponse


aircrafts_router = APIRouter(
    prefix="/aircrafts",
    tags=["v1/aircrafts"],
)


@aircrafts_router.get(
    "/{aircraft_code}",
    response_model=AircraftResponse,
)
async def read_aircraft(
    aircraft_code: str,
    session: AsyncSession = Depends(get_db),
) -> Aircrafts:
    query = (
        select(Aircrafts)
        .where(Aircrafts.aircraft_code == aircraft_code)
    )

    result = await session.execute(query)

    read_aircraft_result = result.scalar_one_or_none()

    if read_aircraft_result is None:
       raise HTTPException(
                status_code=404,
                detail="Aircraft not found"
            )
    return read_aircraft_result
