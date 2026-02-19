from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db_connection import get_db
from app.models.models import Aircrafts
from app.schemas.aircrafts import AircraftCreate, AircraftResponse


v2_aircrafts_router = APIRouter(
    prefix="/aircrafts",
    tags=["v2/aircrafts"],
)


@v2_aircrafts_router.post(
    "/add_aircraft", response_model=AircraftResponse
)
async def create_aircraft(
    aircraft: AircraftCreate, session: AsyncSession = Depends(get_db)
) -> Aircrafts:
    try:
        exist_aircraft = await session.execute(
            select(Aircrafts).where(
                Aircrafts.aircraft_code == aircraft.aircraft_code
            )
        )
        exist_res = exist_aircraft.scalar_one_or_none()

        if exist_res:
            raise HTTPException(
                status_code=400,
                detail=f"Aircraft with code {aircraft.aircraft_code} already exists",
            )

        new_aircraft = Aircrafts(**aircraft.model_dump())

        session.add(new_aircraft)

        await session.commit()
        await session.refresh(new_aircraft)

        return new_aircraft

    except HTTPException:
        raise
    except Exception as err:
        await session.rollback()
        f"Error while creating new aircraft: {str(err)}"
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating aircraft",
        )


@v2_aircrafts_router.delete("/{aircraft_code}", response_model=dict)
async def delete_aircraft(
    aircraft_code: str, session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    stmt = await session.get(Aircrafts, aircraft_code)

    if stmt is None:
        raise HTTPException(
            status_code=404,
            detail=f"Aircraft with code {aircraft_code} not found",
        )

    await session.delete(stmt)

    await session.commit()

    return {
        "message": f"Aircraft {aircraft_code} deleted successfully"
    }
