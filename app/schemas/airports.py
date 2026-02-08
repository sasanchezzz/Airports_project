import re

from pydantic import BaseModel, field_validator

from app.schemas.base import ConditionsMixin


class AirportResponse(BaseModel):
    airport_code: str | None = None
    airport_name: str | None = None
    city: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    timezone: str | None = None


class QPAirports(ConditionsMixin):
    """
    Docstring for QPAirports
    QueryParamAirports as QPAirports
    """
    airport_code: str | None = None
    airport_name: str | None = None
    city: str | None = None
    longitude: float | None = None
    latitude: float | None = None
    timezone: str | None = None

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, tz_param: str) -> str:

        pattern = r'^[A-Z][a-z]+/[A-Z][a-z]+(?:_[A-Z][a-z]+)*$'

        if not re.match(pattern, tz_param):
            raise ValueError(
                f'Invalid timezone format: {tz_param}. '
                f'Expected format: "Continent/City", like "Europe/Moscow"'
            )
        return tz_param
