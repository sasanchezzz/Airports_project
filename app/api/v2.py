from fastapi import APIRouter

from app.api.endpoints.v2.seats import seats_router


router_v2 = APIRouter(
    prefix="/api/v2",
)

router_v2.include_router(seats_router)
