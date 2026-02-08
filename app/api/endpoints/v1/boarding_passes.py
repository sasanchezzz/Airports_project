from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db_connection import get_db
from app.models.models import BoardingPasses
from app.schemas.boarding_passes import BoardingPassesResponse


boarding_passes_router = APIRouter(
    prefix="/boarding_passes",
    tags=["v1/boarding_passes"],
)


@boarding_passes_router.get("/{ticket_no}/{flight_id}", response_model=BoardingPassesResponse)
async def get_ticket_info(
    ticket_no: str,
    flight_id: int,
    session: AsyncSession = Depends(get_db),
) -> BoardingPasses:
    query = (
        select(BoardingPasses)
        .where(
            and_(
                BoardingPasses.ticket_no == ticket_no,
                BoardingPasses.flight_id == flight_id
            )
        )
    )

    result = await session.execute(query)

    ticket_info = result.scalar_one_or_none()

    if ticket_info is None:
       raise HTTPException(
                status_code=404,
                detail="Ticket not found"
            )
    return ticket_info
