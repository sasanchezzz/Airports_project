from fastapi import APIRouter

from app.api.endpoints.v1.aircrafts import aircrafts_router
from app.api.endpoints.v1.airports import airports_router
from app.api.endpoints.v1.boarding_passes import boarding_passes_router
from app.api.endpoints.v1.flights import v1_flights_router


router_v1 = APIRouter(
    prefix="/api/v1",
)

router_v1.include_router(aircrafts_router)
router_v1.include_router(airports_router)
router_v1.include_router(boarding_passes_router)
router_v1.include_router(v1_flights_router)
