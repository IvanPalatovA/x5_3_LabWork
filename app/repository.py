"""Слой доступа к данным (Repository).

Репозиторий отвечает исключительно за хранение и извлечение данных в памяти процесса.
Не содержит бизнес-логики и ничего не знает про HTTP или FastAPI.
"""

from .exceptions import TicketNotFoundError
from .schemas import Ticket


class TicketRepository:
    """Хранит тикеты в памяти процесса."""

    def __init__(self) -> None:
        self._tickets: dict[int, Ticket] = {}
        self._next_id: int = 1

    def add(self, ticket: Ticket) -> Ticket:
        self._tickets[ticket.id] = ticket
        return ticket

    def get(self, ticket_id: int) -> Ticket:
        ticket = self._tickets.get(ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        return ticket

    def list_all(self) -> list[Ticket]:
        return list(self._tickets.values())

    def update(self, ticket: Ticket) -> Ticket:
        if ticket.id not in self._tickets:
            raise TicketNotFoundError(ticket.id)
        self._tickets[ticket.id] = ticket
        return ticket

    def delete(self, ticket_id: int) -> None:
        if ticket_id not in self._tickets:
            raise TicketNotFoundError(ticket_id)
        del self._tickets[ticket_id]

    def next_id(self) -> int:
        ticket_id = self._next_id
        self._next_id += 1
        return ticket_id

