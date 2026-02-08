from pydantic import BaseModel


class SeatsRequest(BaseModel):
    seats_no: str
    fare_conditions: str


class SeatsResponse(BaseModel):
    aircraft_code: str
    seats_no: str
    fare_conditions: str
