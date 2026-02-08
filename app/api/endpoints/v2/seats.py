from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db_connection import get_db
from app.models.models import Seats
from app.schemas.seats import SeatsResponse


seats_router = APIRouter(
    prefix="/seats",
    tags=["v2/seats"],
)

@seats_router.get("/{seat_no}", response_model=SeatsResponse)
async def get_seat_info(
    seat_no: str,
    session: AsyncSession = Depends(get_db),
) -> Seats:
    stmt = (
        select(Seats).
        where(Seats.seat_no == seat_no)
    )

    res = await session.execute(stmt)

    result_get_seat_info = res.scalar_one_or_none()

    if result_get_seat_info is None:
        raise HTTPException(
                status_code=404,
                detail="Seat with {seat_no} number not found"
            )
    return result_get_seat_info
