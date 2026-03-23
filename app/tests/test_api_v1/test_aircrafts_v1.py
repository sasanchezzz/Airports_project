from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Aircrafts
from app.tests.fixtures.data_fixtures import (
    test_aircrafts,
)


class TestReadAircraft:
    """
    Тесты для GET /aircrafts/{aircraft_code}
    """

    async def test_read_aircraft_success(
        self,
        test_client: TestClient,
        aircraft: Aircrafts = test_aircrafts,
    ) -> None:
        """
        Тест успешного получения информации о самолете по коду.

        Проверяет:
        - Статус код 200
        - Корректность возвращаемых данных
        - Соответствие полей модели
        """
        response = test_client.get(
            f"/aircrafts/{aircraft.aircraft_code}"
        )

        assert response.status_code == 200
        data = response.json()

        assert data["aircraft_code"] == aircraft.aircraft_code
        assert data["model"] == aircraft.model
        assert data["range"] == aircraft.range

        assert "aircraft_code" in data
        assert "model" in data
        assert "range" in data
