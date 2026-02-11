from pydantic import BaseModel


class BoardingPassesResponse(BaseModel):
    """
    Модель ответа для таблицы boarding_passes

    Attributes:
        flight_id: int - Уникальный ID рейса

        boarding_no: int - Номер посадочного талона

        seat_no: str - Номер места в самолете, пример: "7A"
    """
    flight_id: int
    boarding_no: int
    seat_no: str
