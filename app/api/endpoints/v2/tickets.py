from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db_connection import get_db
from app.models.models import (
    Bookings,
    Tickets,
    generate_book_ref,
    generate_ticket_no,
)
from app.schemas.tickets import (
    TicketsCreate,
    TicketsResponse,
    TicketsUpdate,
)


v2_tickets_router = APIRouter(
    prefix="/tickets",
    tags=["v2/tickets"],
)


@v2_tickets_router.post(
    "/create_ticket", response_model=TicketsResponse
)
async def create_ticket(
    ticket: TicketsCreate, session: AsyncSession = Depends(get_db)
) -> Tickets:
    async with session.begin():
        if ticket.book_ref:
            book_ref = ticket.book_ref
            booking = await session.get(Bookings, book_ref)
            if not booking:
                raise HTTPException(
                    status_code=404,
                    detail=f"Booking {book_ref} not found",
                )
        else:
            book_ref = generate_book_ref()
            while await session.get(Bookings, book_ref):
                book_ref = generate_book_ref()

            booking = Bookings(
                book_ref=book_ref,
                book_date=datetime.now(timezone.utc),
                total_amount=0,
            )
            session.add(booking)

        ticket_no = generate_ticket_no()
        existing_ticket = await session.get(Tickets, ticket_no)
        while existing_ticket:
            ticket_no = generate_ticket_no()
            existing_ticket = await session.get(Tickets, ticket_no)

        new_ticket = Tickets(
            ticket_no=ticket_no,
            book_ref=book_ref,
            passenger_id=ticket.passenger_id,
            passenger_name=ticket.passenger_name.upper(),
            contact_data=ticket.contact_data,
        )

        session.add(new_ticket)

    await session.refresh(new_ticket)
    return new_ticket


@v2_tickets_router.put("/{ticket_no}", response_model=TicketsResponse)
async def update_ticket(
    ticket_no: str,
    updated_ticket: TicketsUpdate,
    session: AsyncSession = Depends(get_db),
) -> Tickets:
    ticket = await session.get(Tickets, ticket_no)
    if not ticket:
        raise HTTPException(
            status_code=404, detail=f"Ticket {ticket_no} not found"
        )

    ticket.passenger_id = updated_ticket.passenger_id
    ticket.passenger_name = updated_ticket.passenger_name
    ticket.contact_data = updated_ticket.contact_data

    await session.commit()
    await session.refresh(ticket)

    return ticket


@v2_tickets_router.delete("/{ticket_no}", response_model=dict)
async def delete_ticket(
    ticket_no: str, session: AsyncSession = Depends(get_db)
) -> dict[str, str]:
    stmt = await session.get(Tickets, ticket_no)

    if stmt is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket with number {ticket_no} not found",
        )

    await session.delete(stmt)

    await session.commit()

    return {"message": f"Ticket {ticket_no} deleted successfully"}
