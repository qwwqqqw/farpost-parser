"""
Базовый класс для провайдеров cookies
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional

import httpx


class CookiesProvider(ABC):
    """Абстрактный класс для управления cookies"""

    @abstractmethod
    def get(self) -> Dict[str, str]:
        """Получить cookies для запроса"""
        pass

    def update(self, response: httpx.Response) -> None:
        """
        Обновить cookies после запроса.
        По умолчанию — ничего не делать.
        """
        pass

    @abstractmethod
    def handle_block(self):
        """
        Что делать, если cookies заблокированы
        """
        pass
