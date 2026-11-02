"""Конфигурация приложения."""

from functools import lru_cache
from pydantic import BaseModel


class Settings(BaseModel):
    default_page_size: int = 5
    max_page_size: int = 20


@lru_cache
def get_settings() -> Settings:
    return Settings()

