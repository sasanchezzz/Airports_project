import re

from pydantic import BaseModel, field_validator

from app.schemas.mixin import ConditionsMixin


class AirportResponse(BaseModel):
    """
    Модель ответа для таблицы airports
    Attributes:
        airport_code: str - Уникальный код аэропорта, пример: "SVO"

        airport_name: str - Полное название аэропорта

        city: str - Город расположения аэропорта

        longitude: float - Долгота

        latitude: float - Широта

        timezone: str - Часовой пояс, пример: "Europe/Moscow"
    """
    airport_code: str
    airport_name: str
    city: str
    longitude: float
    latitude: float
    timezone: str


class QPAirports(ConditionsMixin):
    """
    Параметры запроса для таблицы airports

    Параметры опциональны, используются только переданные значения
    Attributes:
        airport_code: str | None - Уникальный код аэропорта, пример: "SVO"

        airport_name: str | None - Полное название аэропорта

        city: str | None - Город расположения аэропорта

        longitude: float | None - Долгота

        latitude: float | None - Широта

        timezone: str | None - Часовой пояс, пример: "Europe/Moscow"
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
        """
        Функция-валидотор для проверки формата часового пояса

        Пример: "Континент/Город"

        Слова начинаются с большой буквы, и разделены "/"

        :param tz_param: Строка от пользователя
        :type tz_param: str
        :return: Провалидированная строка
        :rtype: str

        Raises:
            ValueError: У переданной строки неверный формат
        """
        pattern = r'^[A-Z][a-z]+/[A-Z][a-z]+(?:_[A-Z][a-z]+)*$'

        if not re.match(pattern, tz_param):
            raise ValueError(
                f'Invalid timezone format: {tz_param}. '
                f'Expected format: "Continent/City", like "Europe/Moscow"'
            )
        return tz_param
