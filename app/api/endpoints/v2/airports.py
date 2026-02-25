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


@airports_router.post(
    "")