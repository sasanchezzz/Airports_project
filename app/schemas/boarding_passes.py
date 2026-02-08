from pydantic import BaseModel


class BoardingPassesRequest(BaseModel):
    ticket_no: str


class BoardingPassesResponse(BaseModel):
    flight_id: int | None = None
    boarding_no: int | None = None
    seat_no: str
