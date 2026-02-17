from fastapi import APIRouter

from app.api.endpoints.v2.aircrafts import v2_aircrafts_router
from app.api.endpoints.v2.flights import v2_flights_router
from app.api.endpoints.v2.seats import v2_seats_router


router_v2 = APIRouter(
    prefix="/api/v2",
)

router_v2.include_router(v2_seats_router)
router_v2.include_router(v2_flights_router)
router_v2.include_router(v2_aircrafts_router)
