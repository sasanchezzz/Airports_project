from typing import Any

from pydantic import BaseModel

from app.models.base import Base


class ConditionsMixin(BaseModel):
    """
    Docstring for ConditionsMixin
    Generate list[] with query parameters for Pydantic-model
    """
    "def compose_conditions(self: Self, model: Base) -> list[BinaryExpression]:"

    def compose_conditions(self, model: type[Base]) -> list[Any]:
        return [
            getattr(model, query_param) == param_value
            for query_param, param_value in self
            if param_value is not None
        ]
