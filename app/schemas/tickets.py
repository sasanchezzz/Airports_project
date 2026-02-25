import re

from typing import Any

from pydantic import (
    BaseModel,
    ValidatorFunctionWrapHandler,
    field_validator,
)


class TicketsCreate(BaseModel):
    book_ref: str | None = None
    passenger_id: str
    passenger_name: str
    contact_data: dict[str, str]

    @field_validator("passenger_id", mode="wrap")
    @classmethod
    def check_passenger_id(
        cls, value: Any, handler: ValidatorFunctionWrapHandler
    ) -> str:
        """
        Валидатор для поля passanger_id

        Проверяет что строка будет соответствовать формату '1234 567890'

        Строка принимает только 10 цифр, в формате: 4 цифры, пробел, 6 цифр

        :param value: Значение от клиента
        :type value: Any
        :param handler: Функция-обработчик для стандартной валидации
        :type handler: ValidatorFunctionWrapHandler
        :return: Провалидированное значение
        :rtype: str
        """
        try:
            result = handler(value)

            if not isinstance(result, str):
                raise ValueError("Passenger_id must be string")

            clean_value = result.strip()
            if not re.match(r"^\d{4}\s\d{6}$", clean_value):
                raise ValueError(
                    f"Must be format '1234 567890', got '{clean_value}'"
                )
            return clean_value

        except Exception:
            if isinstance(value, (int, float)):
                str_val = str(int(value)).zfill(10)
                if len(str_val) == 10:
                    return cls.check_passenger_id(
                        f"{str_val[:4]} {str_val[4:]}",
                        handler,
                    )

            elif isinstance(value, str):
                digits_only = re.sub(r"\s+", "", value.strip())
                if re.match(r"^\d{10}$", digits_only):
                    return cls.check_passenger_id(
                        f"{digits_only[:4]} {digits_only[4:]}",
                        handler,
                    )
            raise ValueError(
                f"Invalid value for passenger_id: '{value}'. Expected format: '1234 567890'"
            )

    @field_validator("passenger_name", mode="after")
    @classmethod
    def check_passenger_name(cls, value: str) -> str:
        """
        Валидатор для поля passenger_name

        Проверяет что строка будет соответствовать формату 'NAME SURNAME' или 'NAME SURNAME1-SURNAME2'

        :param value: Значение от клиента, после валидации от pydantic
        :type value: str
        :return: Провалидированное значение
        :rtype: str
        """

        if not value:
            raise ValueError("Passenger_name can't be empty!")

        if not isinstance(value, str):
            raise ValueError("Passenger_name must be a string!")

        value = value.strip()

        if not re.match(r"^[A-Za-z]+ [A-Za-z]+(-[A-Za-z]+)?$", value):
            raise ValueError(
                "Passenger_name must be in format: 'NAME SURNAME' or 'NAME SURNAME1-SURNAME2'"
            )

        return value.upper()

    @field_validator("contact_data", mode="after")
    @classmethod
    def check_contact_data(
        cls, value: dict[str, str]
    ) -> dict[str, str]:
        """
        Валидатор для поля contact_data

        Проверяет что строка будет соответствовать формату:
        - {"email": "test@example.ru"}
        - {"phone": "+12345678910"}
        - {"email": "test@example.ru", "phone": "+12345678910"}

        :param value: Значение от клиента, после валидации от pydantic
        :type value: dict[str, str]
        :return: Провалидированное значение
        :rtype: dict[str, str]
        """
        if value is None:
            raise ValueError("Contact_data can't be empty!")

        # if not isinstance(value, dict):
        #     raise ValueError("Contact_data must be dictionary!")

        required_keys = {"email", "phone"}
        for key in value.keys():
            if key not in required_keys:
                raise ValueError(
                    "Contact_data can contain only 'email' and 'phone'!"
                )

        if "email" in value:
            email = value["email"]
            if not isinstance(email, str):
                raise ValueError("Email value must be a string!")
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                raise ValueError(f"Invalid format for email: {email}")

        if "phone" in value:
            phone = value["phone"]
            if not isinstance(phone, str):
                raise ValueError("Phone value must be a string!")
            if not re.match(r"^\+\d{10,15}$", phone):
                raise ValueError(
                    f"Phone must start with '+' and contain 10-15 numbers, got {phone}"
                )

        return value


class TicketsUpdate(BaseModel):
    passenger_id: str
    passenger_name: str
    contact_data: dict[str, str]

    @field_validator("passenger_id", mode="wrap")
    @classmethod
    def check_passenger_id(
        cls, value: Any, handler: ValidatorFunctionWrapHandler
    ) -> str:
        """
        Валидатор для поля passanger_id

        Проверяет что строка будет соответствовать формату '1234 567890'

        Строка принимает только 10 цифр, в формате: 4 цифры, пробел, 6 цифр

        :param value: Значение от клиента
        :type value: Any
        :param handler: Функция-обработчик для стандартной валидации
        :type handler: ValidatorFunctionWrapHandler
        :return: Провалидированное значение
        :rtype: str
        """
        try:
            result = handler(value)

            if not isinstance(result, str):
                raise ValueError("Passenger_id must be string")

            clean_value = result.strip()
            if not re.match(r"^\d{4}\s\d{6}$", clean_value):
                raise ValueError(
                    f"Must be format '1234 567890', got '{clean_value}'"
                )
            return clean_value

        except Exception:
            if isinstance(value, (int, float)):
                str_val = str(int(value)).zfill(10)
                if len(str_val) == 10:
                    return cls.check_passenger_id(
                        f"{str_val[:4]} {str_val[4:]}",
                        handler,
                    )

            elif isinstance(value, str):
                digits_only = re.sub(r"\s+", "", value.strip())
                if re.match(r"^\d{10}$", digits_only):
                    return cls.check_passenger_id(
                        f"{digits_only[:4]} {digits_only[4:]}",
                        handler,
                    )
            raise ValueError(
                f"Invalid value for passenger_id: '{value}'. Expected format: '1234 567890'"
            )

    @field_validator("passenger_name", mode="after")
    @classmethod
    def check_passenger_name(cls, value: str) -> str:
        """
        Валидатор для поля passenger_name

        Проверяет что строка будет соответствовать формату 'NAME SURNAME' или 'NAME SURNAME1-SURNAME2'

        :param value: Значение от клиента, после валидации от pydantic
        :type value: str
        :return: Провалидированное значение
        :rtype: str
        """

        if not value:
            raise ValueError("Passenger_name can't be empty!")

        if not isinstance(value, str):
            raise ValueError("Passenger_name must be a string!")

        value = value.strip()

        if not re.match(r"^[A-Za-z]+ [A-Za-z]+(-[A-Za-z]+)?$", value):
            raise ValueError(
                "Passenger_name must be in format: 'NAME SURNAME' or 'NAME SURNAME1-SURNAME2'"
            )

        return value.upper()

    @field_validator("contact_data", mode="after")
    @classmethod
    def check_contact_data(
        cls, value: dict[str, str]
    ) -> dict[str, str]:
        """
        Валидатор для поля contact_data

        Проверяет что строка будет соответствовать формату:
        - {"email": "test@example.ru"}
        - {"phone": "+12345678910"}
        - {"email": "test@example.ru", "phone": "+12345678910"}

        :param value: Значение от клиента, после валидации от pydantic
        :type value: dict[str, str]
        :return: Провалидированное значение
        :rtype: dict[str, str]
        """
        if value is None:
            raise ValueError("Contact_data can't be empty!")

        # if not isinstance(value, dict):
        #     raise ValueError("Contact_data must be dictionary!")

        required_keys = {"email", "phone"}
        for key in value.keys():
            if key not in required_keys:
                raise ValueError(
                    "Contact_data can contain only 'email' and 'phone'!"
                )

        if "email" in value:
            email = value["email"]
            if not isinstance(email, str):
                raise ValueError("Email value must be a string!")
            if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
                raise ValueError(f"Invalid format for email: {email}")

        if "phone" in value:
            phone = value["phone"]
            if not isinstance(phone, str):
                raise ValueError("Phone value must be a string!")
            if not re.match(r"^\+\d{10,15}$", phone):
                raise ValueError(
                    f"Phone must start with '+' and contain 10-15 numbers, got {phone}"
                )

        return value


class TicketsResponse(BaseModel):
    ticket_no: str
    book_ref: str
    passenger_id: str
    passenger_name: str
    contact_data: dict[str, str]

    @field_validator("book_ref", mode="after")
    @classmethod
    def check_book_ref(cls, value: str) -> str:
        """
        Валидатор для поля book_ref

        Проверяет что строка будет соответствовать формату 'ABC123'

        :param value: Передаваемое значение
        :type value: str
        :return: Провалидированное значение
        :rtype: str
        """
        if len(value) != 6:
            raise ValueError(
                f"Book_ref must be exactly 6 characters, got {len(value)}"
            )

        if not re.match(r"^[A-Z0-9]+$", value):
            raise ValueError(
                f"Book_ref must contain only uppercase letters and numbers, got '{value}'"
            )

        return value
