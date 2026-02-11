from typing import Any

from pydantic import BaseModel

from app.models.base import Base


class ConditionsMixin(BaseModel):
    """
    Миксин, который создает список с параметрами запроса для Pydantic-model
    """

    def compose_conditions(self, model: type[Base]) -> list[Any]:
        """
        Функция для создания фильтров запроса

        :param self: Передает ConditionsMixin
        :param model: Передает SQLAlchemy модель
        :type model: type[Base]
        :return: Возвращает список условий с параметрами переданной модели
        :rtype: list[Any]
        """
        return [
            getattr(model, query_param) == param_value
            for query_param, param_value in self
            if param_value is not None
        ]
