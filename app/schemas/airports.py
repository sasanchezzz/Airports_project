import re

from typing import Any

from pydantic import (
    BaseModel,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)

from app.schemas.mixin import ConditionsMixin


class AirportsResponse(BaseModel):
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


class AirportsUpsertResponse(BaseModel):
    message: str
    airports: list[AirportsResponse]


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

    @field_validator("timezone")
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
        pattern = r"^[A-Z][a-z]+/[A-Z][a-z]+(?:_[A-Z][a-z]+)*$"

        if not re.match(pattern, tz_param):
            raise ValueError(
                f"Invalid timezone format: {tz_param}. "
                f'Expected format: "Continent/City", like "Europe/Moscow"'
            )
        return tz_param


class AirportsUpsert(BaseModel):
    airport_code: str
    airport_name: str
    city: str
    longitude: float
    latitude: float
    timezone: str

    @field_validator("airport_code", mode="wrap")
    @classmethod
    def validate_airport_code(
        cls, value: Any, handler: ValidatorFunctionWrapHandler
    ) -> str:
        """
        Валидатор для поля airport_code

        Проверяет что строка будет соответствовать формату 'ABC'

        :param value: Значение от клиента
        :type value: Any
        :param handler: Функция-обработчик для стандартной валидации
        :type handler: ValidatorFunctionWrapHandler
        :return: Провалидированное значение
        :rtype: str
        """
        try:
            valid_value = handler(value)

            if not isinstance(valid_value, str):
                raise ValueError("Airport_code must be a string")

            valid_value = valid_value.upper()

            if not re.match(r"^[A-Z]+$", valid_value):
                raise ValueError(
                    "Airport_code must contain uppercase english letters, example: ABC"
                )

            return valid_value

        except Exception as err:
            if isinstance(value, int):
                raise ValueError(
                    f"Airport_code must be string, got {value}"
                )
            if isinstance(value, str) and value.islower():
                return cls.validate_airport_code(
                    value.upper(), handler
                )
            raise ValueError(f"Invalid aircraft_code: {err}")

    @field_validator("airport_name", "city", mode="before")
    @classmethod
    def validate_cities_names(
        cls, value: Any, info: ValidationInfo
    ) -> str:
        """
        Валидатор для полей airport_name и city

        Проверяет что:
        - Первая буква заглавная, остальные строчные
        - Разрешены дефисы, пример: "Ростов-на-Дону", "Оренбург-Центральный"
        - Разрешен предлог "на" (только в нижнем регистре через дефис)
        - Только русские буквы, дефисы и пробелы
        - Запрещены цифры и спецсимволы, кроме дефиса

        :param value: Значение от клиента
        :type value: Any
        :param info: Дополнительная информация об уже проверенных данных
        :type info: ValidationInfo
        :return: Провалидированное значение
        :rtype: str
        """
        field_name = info.field_name

        if not value or not isinstance(value, str):
            raise ValueError(
                f"{field_name} must be a non-empty string"
            )

        clean_value = value.strip()

        if len(clean_value) < 2:
            raise ValueError(
                f"{field_name} is too short, got {clean_value}"
            )

        if not re.match(r"^[А-ЯЁа-яё\s\-]+$", clean_value):
            raise ValueError(
                f"{field_name} must contain only Russian letters, spaces and hyphens, "
                f"got '{clean_value}'"
            )

        words = clean_value.split()
        processed_words = []

        for word in words:
            if "-" in word:
                parts = word.split("-")
                processed_parts = []

                for i, part in enumerate(parts):
                    if (
                        part.lower() == "на" and i > 0
                    ):  # "на" только не в начале
                        processed_parts.append("на")
                    else:
                        # Первая буква заглавная, остальные строчные
                        if len(part) > 1:
                            processed_parts.append(
                                part[0].upper() + part[1:].lower()
                            )
                        else:
                            processed_parts.append(part.upper())

                processed_words.append("-".join(processed_parts))
            else:
                # Обычное слово: первая буква заглавная, остальные строчные
                if len(word) > 1:
                    processed_words.append(
                        word[0].upper() + word[1:].lower()
                    )
                else:
                    processed_words.append(word.upper())

        result = " ".join(processed_words)
        if field_name == "city":
            # Для города: не должен содержать указание на аэропорт
            forbidden_words = [
                "аэропорт",
                "airport",
                "терминал",
                "центральный",
            ]
            lower_result = result.lower()
            for word in forbidden_words:
                if word in lower_result:
                    raise ValueError(
                        f"City name should not contain '{word}'"
                    )

        elif field_name == "airport_name":
            # Для аэропорта: базовые проверки
            if (
                len(result.split()) > 3
            ):  # Не более 3 слов в названии аэропорта
                raise ValueError(
                    f"Airport name is too long: '{result}'"
                )

        return result

    @field_validator("timezone")
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
        pattern = r"^[A-Z][a-z]+/[A-Z][a-z]+(?:_[A-Z][a-z]+)*$"

        if not re.match(pattern, tz_param):
            raise ValueError(
                f"Invalid timezone format: {tz_param}. "
                f'Expected format: "Continent/City", like "Europe/Moscow"'
            )
        return tz_param
