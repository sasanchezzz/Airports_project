from pydantic import BaseModel


class AircraftResponse(BaseModel):
    aircraft_code: str
    model: str
    range: int
