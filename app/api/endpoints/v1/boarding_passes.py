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


@boarding_passes_router.get(
    "/{ticket_no}",
    response_model=BoardingPassesResponse,
    summary="Get information about boarding pass",
    response_description="Boarding pass information",
)
async def get_ticket_info(
    ticket_no: str,
    session: AsyncSession = Depends(get_db),
) -> BoardingPasses:
    """
    Получение информации о посадочном талоне по номеру билета

    Параметры запроса:
    - **ticket_no**: уникальный номер билета

    Параметры ответа:
    - **flight_id**: id полета
    - **boarding_no**: номер посадочного талона
    - **seat_no**: номер места в самолете
    """

    query = select(BoardingPasses).where(
        and_(
            BoardingPasses.ticket_no == ticket_no,
        )
    )

    result = await session.execute(query)

    ticket_info = result.scalar_one_or_none()

    if ticket_info is None:
        raise HTTPException(
            status_code=404,
            detail=f"Boarding pass with ticket number {ticket_no} - not found",
        )
    return ticket_info
