"""Слой бизнес-логики (Service).

Инкапсулирует бизнес-правила:
- валидацию переходов статуса согласно ALLOWED_TRANSITIONS;
- вычисление системных полей при создании тикета (id, status, created_at);
- сортировку тикетов по приоритету (по весам) и по дате создания;
- пагинацию с ограничениями из настроек (default_page_size, max_page_size).
Сервис не зависит от FastAPI и не использует HTTPException.
"""

from datetime import datetime

from .config import Settings
from .exceptions import InvalidStatusTransitionError
from .repository import TicketRepository
from .schemas import (
    ALLOWED_TRANSITIONS,
    Priority,
    Ticket,
    TicketCreate,
    TicketPage,
    TicketStatus,
    TicketUpdate,
)

PRIORITY_WEIGHTS: dict[Priority, int] = {
    Priority.low: 1,
    Priority.normal: 2,
    Priority.high: 3,
    Priority.urgent: 4,
}


class TicketService:
    def __init__(self, repository: TicketRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    def create_ticket(self, payload: TicketCreate) -> Ticket:
        ticket_id = self._repository.next_id()
        ticket = Ticket(
            id=ticket_id,
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            status=TicketStatus.open,
            assignee=payload.assignee,
            created_at=datetime.now(),
        )
        return self._repository.add(ticket)

    def get_ticket(self, ticket_id: int) -> Ticket:
        return self._repository.get(ticket_id)

    def list_tickets(
        self,
        sort_by: str = "created_at",
        order: str = "desc",
        page: int = 1,
        page_size: int | None = None,
    ) -> TicketPage:
        # Применяем page_size по умолчанию из settings и ограничиваем settings.max_page_size
        if page_size is None or page_size < 1:
            effective_page_size = self._settings.default_page_size
        else:
            effective_page_size = min(page_size, self._settings.max_page_size)

        effective_page = max(1, page)

        tickets = self._repository.list_all()

        reverse = (order == "desc")
        if sort_by == "priority":
            tickets.sort(
                key=lambda t: (PRIORITY_WEIGHTS.get(t.priority, 0), t.created_at),
                reverse=reverse,
            )
        else:
            tickets.sort(key=lambda t: t.created_at, reverse=reverse)

        total = len(tickets)
        offset = (effective_page - 1) * effective_page_size
        items = tickets[offset : offset + effective_page_size]

        return TicketPage(
            items=items,
            total=total,
            page=effective_page,
            page_size=effective_page_size,
        )

    def update_ticket(self, ticket_id: int, changes: TicketUpdate) -> Ticket:
        ticket = self._repository.get(ticket_id)
        update_data = changes.model_dump(exclude_unset=True)

        if "status" in update_data and update_data["status"] is not None:
            target_status = update_data["status"]
            if target_status != ticket.status:
                allowed = ALLOWED_TRANSITIONS.get(ticket.status, set())
                if target_status not in allowed:
                    raise InvalidStatusTransitionError(ticket.status, target_status)

        updated_ticket = ticket.model_copy(update=update_data)
        return self._repository.update(updated_ticket)

    def delete_ticket(self, ticket_id: int) -> None:
        self._repository.delete(ticket_id)

