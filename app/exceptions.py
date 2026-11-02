"""Собственные исключения сервиса HelpDesk.

Исключения являются частью доменной модели и не зависят от FastAPI или HTTP.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .schemas import TicketStatus


class HelpDeskError(Exception):
    """Базовое исключение сервиса."""


class TicketNotFoundError(HelpDeskError):
    """Выбрасывается, когда тикет с указанным id не найден."""

    def __init__(self, ticket_id: int) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Тикет {ticket_id} не найден")


class InvalidStatusTransitionError(HelpDeskError):
    """Выбрасывается при попытке выполнить запрещённый переход статуса тикета."""

    def __init__(self, current: "TicketStatus", target: "TicketStatus") -> None:
        self.current = current
        self.target = target
        curr_str = current.value if hasattr(current, "value") else str(current)
        targ_str = target.value if hasattr(target, "value") else str(target)
        super().__init__(f"Переход {curr_str} -> {targ_str} запрещён")
