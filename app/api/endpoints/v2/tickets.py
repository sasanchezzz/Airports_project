from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db_connection import get_db
from app.models.models import 
from app.schemas.aircrafts import 


v2_tickets_router = APIRouter(
    prefix="/tickets",
    tags=["v2/tickets"],
)

@v2_tickets_router.post(
    "/create", response_model=)