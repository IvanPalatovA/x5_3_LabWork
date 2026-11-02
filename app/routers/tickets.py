"""Тонкий HTTP-роутер для работы с тикетами техподдержки (/tickets).

Каждый эндпоинт производит разбор параметров HTTP-запроса и делегирует выполнение
соответствующему методу TicketService.
Внутри роутера отсутствует бизнес-логика, циклы for, проверки статусов и raise HTTPException.
"""

from fastapi import APIRouter, Query, status

from ..dependencies import ServiceDep
from ..schemas import Ticket, TicketCreate, TicketPage, TicketUpdate

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post(
    "",
    response_model=Ticket,
    status_code=status.HTTP_201_CREATED,
    summary="Создать тикет",
)
def create_ticket(
    payload: TicketCreate,
    service: ServiceDep,
) -> Ticket:
    return service.create_ticket(payload)


@router.get(
    "",
    response_model=TicketPage,
    summary="Получить список тикетов",
)
def list_tickets(
    service: ServiceDep,
    sort_by: str = Query("created_at", pattern="^(created_at|priority)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int | None = Query(None, ge=1),
) -> TicketPage:
    return service.list_tickets(
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{ticket_id}",
    response_model=Ticket,
    summary="Получить тикет по id",
)
def get_ticket(
    ticket_id: int,
    service: ServiceDep,
) -> Ticket:
    return service.get_ticket(ticket_id)


@router.patch(
    "/{ticket_id}",
    response_model=Ticket,
    summary="Изменить часть данных тикета",
)
def update_ticket(
    ticket_id: int,
    changes: TicketUpdate,
    service: ServiceDep,
) -> Ticket:
    return service.update_ticket(ticket_id, changes)


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить тикет",
)
def delete_ticket(
    ticket_id: int,
    service: ServiceDep,
) -> None:
    service.delete_ticket(ticket_id)
