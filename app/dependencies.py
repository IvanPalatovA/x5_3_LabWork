"""Внедрение зависимостей FastAPI (Dependencies).

Определяет цепочку зависимостей:
Settings -> TicketRepository -> TicketService.
Репозиторий закеширован с помощью @lru_cache для сохранения состояния в памяти процесса.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from .config import Settings, get_settings
from .repository import TicketRepository
from .service import TicketService


@lru_cache
def get_repository() -> TicketRepository:
    """Возвращает singleton экземпляр репозитория тикетов."""
    return TicketRepository()


def get_service(
    repository: TicketRepository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> TicketService:
    """Создает и возвращает экземпляр TicketService."""
    return TicketService(repository, settings)


SettingsDep = Annotated[Settings, Depends(get_settings)]
ServiceDep = Annotated[TicketService, Depends(get_service)]
