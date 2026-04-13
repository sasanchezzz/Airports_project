from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import pytest_asyncio

from app.models.models import Bookings, Tickets


@pytest_asyncio.fixture
async def test_tickets_v2(
    session: AsyncSession,
) -> dict:
    """
    Создание тестовых данных для таблицы Tickets (v2)
    """
    booking = Bookings(
        book_ref="TST001",
        total_amount=15000.00,
    )
    session.add(booking)
    await session.commit()

    ticket = Tickets(
        ticket_no="1234567890123",
        book_ref="TST001",
        passenger_id="1234 567890",
        passenger_name="IVAN IVANOV",
        contact_data={
            "phone": "+79001234567",
            "email": "ivan@test.com",
        },
    )
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)

    return {
        "ticket_no": ticket.ticket_no,
        "book_ref": "TST001",
        "passenger_id": "1234 567890",
        "passenger_name": "IVAN IVANOV",
    }


class TestCreateTicket:
    """
    Тесты для POST /tickets/create_ticket
    """

    async def test_create_ticket_with_new_booking(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест создания билета с новым бронированием.

        Проверяет:
        - Статус код 200
        - Сгенерированный ticket_no
        - Сгенерированный book_ref
        """
        payload = {
            "passenger_id": "1234 567890",
            "passenger_name": "PETR PETROV",
            "contact_data": {
                "phone": "+79009876543",
                "email": "petr@test.com",
            },
        }

        response = await async_client.post(
            "/api/v2/tickets/create_ticket", json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert "ticket_no" in data
        assert len(data["ticket_no"]) == 13
        assert "book_ref" in data
        assert data["passenger_name"] == "PETR PETROV"

    async def test_create_ticket_existing_booking(
        self,
        async_client: AsyncClient,
        test_tickets_v2: dict,
    ) -> None:
        """
        Тест создания билета с существующим бронированием.

        Проверяет:
        - Статус код 200
        - Использование указанного book_ref
        """
        payload = {
            "book_ref": test_tickets_v2["book_ref"],
            "passenger_id": "9876 543210",
            "passenger_name": "ANNA SIDOROVA",
            "contact_data": {"phone": "+79001112233"},
        }

        response = await async_client.post(
            "/api/v2/tickets/create_ticket", json=payload
        )

        assert response.status_code == 200
        data = response.json()

        assert data["book_ref"] == test_tickets_v2["book_ref"]
        assert data["passenger_name"] == "ANNA SIDOROVA"

    async def test_create_ticket_booking_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест создания билета с несуществующим бронированием.

        Проверяет:
        - Статус код 404
        """
        payload = {
            "book_ref": "NONEXIST",
            "passenger_id": "1234 567890",
            "passenger_name": "TEST USER",
            "contact_data": {"phone": "+79000000000"},
        }

        response = await async_client.post(
            "/api/v2/tickets/create_ticket", json=payload
        )

        assert response.status_code == 404


class TestUpdateTicket:
    """
    Тесты для PUT /tickets/{ticket_no}
    """

    async def test_update_ticket_success(
        self,
        async_client: AsyncClient,
        test_tickets_v2: dict,
    ) -> None:
        """
        Тест успешного обновления билета.

        Проверяет:
        - Статус код 200
        - Обновленные данные
        """
        payload = {
            "passenger_id": "1111 222222",
            "passenger_name": "Ivan Ivanov",
            "contact_data": {
                "phone": "+79009998877",
                "email": "new@test.com",
            },
        }

        response = await async_client.put(
            f"/api/v2/tickets/{test_tickets_v2['ticket_no']}",
            json=payload,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["passenger_id"] == "1111 222222"
        assert data["passenger_name"] == "IVAN IVANOV"

    async def test_update_ticket_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест обновления несуществующего билета.

        Проверяет:
        - Статус код 404
        """
        payload = {
            "passenger_id": "1234 567890",
            "passenger_name": "Nobody Noby",
            "contact_data": {
                "phone": "+79000000000",
                "email": "nobody@test.com",
            },
        }

        response = await async_client.put(
            "/api/v2/tickets/0000000000000", json=payload
        )

        assert response.status_code == 404


class TestDeleteTicket:
    """
    Тесты для DELETE /tickets/{ticket_no}
    """

    async def test_delete_ticket_success(
        self,
        async_client: AsyncClient,
        test_tickets_v2: dict,
    ) -> None:
        """
        Тест успешного удаления билета.

        Проверяет:
        - Статус код 200
        - Сообщение об успешном удалении
        """
        response = await async_client.delete(
            f"/api/v2/tickets/{test_tickets_v2['ticket_no']}"
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert test_tickets_v2["ticket_no"] in data["message"]

    async def test_delete_ticket_not_found(
        self,
        async_client: AsyncClient,
    ) -> None:
        """
        Тест удаления несуществующего билета.

        Проверяет:
        - Статус код 404
        """
        response = await async_client.delete(
            "/api/v2/tickets/0000000000000"
        )

        assert response.status_code == 404
