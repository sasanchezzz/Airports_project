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
    "/upsert",
    response_model=AirportsUpsertResponse,
    summary="Upsert new airport",
    response_description="Upserted airport",
)
async def airports_upsert(
    airports: list[AirportsUpsert],
    session: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Создание и обновление нескольких аэропортов по заданным параметрам

    Тело запроса:
    - **airport_code**: уникальный код самолета
    - **airport_name**: уникальный код самолета
    - **city**: модель самолета
    - **longitude**: максимальная дальность полета самолета
    - **latitude**: максимальная дальность полета самолета
    - **timezone**: максимальная дальность полета самолета

    Параметры ответа:
    - **message**: уведомление об успешном внесении данных
    - **airports**: список внесенных данных о самолетах из тела запроса
    """

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


@v2_airports_router.delete(
    "/{airport_code}",
    response_model=dict,
    summary="Delete airport",
    response_description="Deleted airport",
)
async def delete_airport(
    airport_code: str, session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    """
    Удаление аэропорта по заданному коду

    Параметры запроса:
    - **airport_code**: код аэропорта, который нужно удалить

    Параметры ответа:
    - **message**: уведомление об успешном удалении аэропорта с заданным кодом
    """

    stmt = await session.get(Airports, airport_code)

    if stmt is None:
        raise HTTPException(
            status_code=404,
            detail=f"Airport with code {airport_code} not found",
        )

    await session.delete(stmt)

    await session.commit()

    return {"message": f"Airport {airport_code} deleted successfully"}
