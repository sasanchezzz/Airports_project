from pydantic import BaseModel

from app.schemas.base import ConditionsMixin


class SeatsResponse(BaseModel):
    aircraft_code: str
    seat_no: str
    fare_conditions: str

class QPSeats(ConditionsMixin):
    seat_no: str | None = None
    fare_conditions: str | None = None
