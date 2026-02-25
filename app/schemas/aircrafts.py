import re

from typing import Any

from pydantic import (
    BaseModel,
    ValidatorFunctionWrapHandler,
    field_validator,
)

from app.models.enums import AircraftModelType


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


class AircraftCreate(BaseModel):
    """
    Модель для создания записи для таблицы aircrafts

    Attributes:
        aircraft_code: str - Уникальный код самолета, пример: "CN1" или "773"

        model: AircraftModelType (enum) - Модель самолета, пример: "Boeing 777-300"

        range: int - Максимальная дальность полета самолета в километрах
    """

    aircraft_code: str
    model: AircraftModelType
    range: int

    @field_validator("aircraft_code", mode="wrap")
    @classmethod
    def check_aircraft_code(
        cls, value: Any, handler: ValidatorFunctionWrapHandler
    ) -> str:
        """
        Валидатор для поля aircraft_code

        Проверяет что строка будет состоять из цифр и английских букв в верхнем регистре

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
                raise ValueError("Aircraft_code must be a string")

            valid_value = valid_value.upper()

            if not re.match(r"^[A-Z0-9]+$", valid_value):
                raise ValueError(
                    "Aircraft_code must contain numbers or uppercase english letters, example: 123, 1A1, ABC"
                )

            return valid_value

        except Exception as err:
            if isinstance(value, int):
                str_value = str(value)
                return cls.check_aircraft_code(str_value, handler)
            if isinstance(value, str) and value.islower():
                return cls.check_aircraft_code(value.upper(), handler)
            raise ValueError(f"Invalid aircraft_code: {err}")

    @field_validator("range", mode="before")
    @classmethod
    def check_range(cls, value: Any) -> int:
        """
        Валидатор для поля range

        Проверяет что значение, будет числом в диапазоне от 1000 до 19000

        :param value: Приходящее значение
        :type value: Any
        :return: Провалидированное значение
        :rtype: int
        """
        if not isinstance(value, int):
            raise ValueError(
                f"Range value must be a number, got {value}"
            )

        min_range = 1000
        max_range = 19000

        if value < min_range:
            raise ValueError(
                f"Range value must be more than {min_range}, got {value}"
            )
        if value > max_range:
            raise ValueError(
                f"Range value must be less than {max_range}, got {value}"
            )

        return value


class AircraftRangePatch(BaseModel):
    range: int

    @field_validator("range", mode="before")
    @classmethod
    def validate_range(cls, value: Any) -> int:
        """
        Валидатор для поля range
        """
        match value:
            case int(num) if 1000 <= num <= 19000:
                return num
            case int(num) if num < 1000:
                raise ValueError(
                    f"Range value must be more than 1000, got {num}"
                )
            case int(num) if num > 19000:
                raise ValueError(
                    f"Range value must be less than 19000, got {num}"
                )
            case str(s):
                try:
                    return cls.validate_range(int(s))
                except ValueError:
                    raise ValueError(
                        f"Range must be a number, got string '{s}'"
                    )
            case float(f):
                return cls.validate_range(int(f))
            case _:
                raise ValueError("Range must be a number")
