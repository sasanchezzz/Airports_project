from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_connection import get_db
from app.models.models import Airports
from app.schemas.airports import (
    AirportsUpsert,
    AirportsUpsertResponse,
)


v2_airports_router = APIRouter(
    prefix="/airports",
    tags=["v2/airports"],
)


@v2_airports_router.post(
    "/upsert", response_model=AirportsUpsertResponse
)
async def airports_upsert(
    airports: list[AirportsUpsert],
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    airports_data = [airport.model_dump() for airport in airports]

    stmt = await session.execute(
        insert(Airports)
        .values(airports_data)
        .on_conflict_do_update(
            index_elements=["airport_code"],
            set_={
                "airport_name": insert(
                    Airports
                ).excluded.airport_name,
                "city": insert(Airports).excluded.city,
                "longitude": insert(Airports).excluded.longitude,
                "latitude": insert(Airports).excluded.latitude,
                "timezone": insert(Airports).excluded.timezone,
            },
        )
        .returning(Airports)
    )

    await session.commit()

    upserted_airport = stmt.scalars().all()

    return {
        "message": f"Successfully upserted {len(upserted_airport)} airports",
        "airports": upserted_airport,
    }


@v2_airports_router.delete("/{airport_code}", response_model=dict)
async def delete_airport(
    airport_code: str, session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    stmt = await session.get(Airports, airport_code)

    if stmt is None:
        raise HTTPException(
            status_code=404,
            detail=f"Airport with code {airport_code} not found",
        )

    await session.delete(stmt)

    await session.commit()

    return {"message": f"Airport {airport_code} deleted successfully"}
