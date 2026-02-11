from pydantic import BaseModel

from app.schemas.mixin import ConditionsMixin


class SeatsResponse(BaseModel):
    """
    Модель ответа таблицы seats для эндпоинтов
    """
    aircraft_code: str
    seat_no: str
    fare_conditions: str

class QPSeats(ConditionsMixin):
    """
    Параметры запроса для таблицы seats
    """
    seat_no: str | None = None
    fare_conditions: str | None = None
