from pydantic import BaseModel


class AircraftResponse(BaseModel):
    """
    Модель ответа для таблицы aircrafts

    Attributes:
        aircraft_code: str - Уникальный код самолета, пример: "CN1" или "773"

        model: str - Модель самолета, пример: "Boeing 777-300"

        range: int - Максимальная дальность полета самолета в километрах
    """
    aircraft_code: str
    model: str
    range: int
