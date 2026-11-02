"""Схемы данных Pydantic и перечисления сервиса тикетов техподдержки."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Priority(str, Enum):
    low = "low"
    normal = "normal"
    high = "high"
    urgent = "urgent"


class TicketStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


ALLOWED_TRANSITIONS: dict[TicketStatus, set[TicketStatus]] = {
    TicketStatus.open: {TicketStatus.in_progress},
    TicketStatus.in_progress: {TicketStatus.resolved, TicketStatus.open},
    TicketStatus.resolved: {TicketStatus.closed, TicketStatus.in_progress},
    TicketStatus.closed: set(),
}


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, description="Название тикета (обязательное поле)")
    description: str | None = Field(default=None, description="Описание проблемы")
    priority: Priority = Field(default=Priority.normal, description="Приоритет тикета")
    assignee: str | None = Field(default=None, description="Исполнитель тикета")


class TicketUpdate(BaseModel):
    description: str | None = Field(default=None, description="Обновленное описание")
    priority: Priority | None = Field(default=None, description="Обновленный приоритет")
    assignee: str | None = Field(default=None, description="Обновленный исполнитель")
    status: TicketStatus | None = Field(
        default=None,
        description="Новый статус тикета (проверяется по правилам переходов)",
    )


class Ticket(BaseModel):
    id: int = Field(description="Уникальный идентификатор тикета")
    title: str = Field(description="Название тикета")
    description: str | None = Field(default=None, description="Описание проблемы")
    priority: Priority = Field(description="Приоритет тикета")
    status: TicketStatus = Field(description="Текущий статус тикета")
    assignee: str | None = Field(default=None, description="Исполнитель тикета")
    created_at: datetime = Field(description="Дата и время создания тикета")


class TicketPage(BaseModel):
    items: list[Ticket] = Field(description="Список тикетов текущей страницы")
    total: int = Field(description="Общее количество тикетов")
    page: int = Field(description="Номер текущей страницы")
    page_size: int = Field(description="Размер страницы")

