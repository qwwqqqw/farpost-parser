"""
Провайдер cookies из собственного файла
"""
import json
from pathlib import Path
from typing import Dict

from loguru import logger

from .base import CookiesProvider


class OwnCookiesProvider(CookiesProvider):
    """Использует cookies из локального файла"""

    def __init__(self, storage_path: str | Path = "storage/own_cookies.json"):
        self.storage_path = Path(storage_path)

    def get(self) -> Dict[str, str]:
        """Загружает cookies из файла"""
        try:
            if not self.storage_path.exists():
                logger.warning(f"Файл cookies не найден: {self.storage_path}")
                return {}

            with open(self.storage_path, "r", encoding="utf-8") as f:
                cookies_data = json.load(f)

            # Поддерживаем несколько форматов
            if isinstance(cookies_data, dict) and "cookies" in cookies_data:
                cookies_data = cookies_data["cookies"]

            # Преобразуем в словарь {name: value}
            cookies = {}
            if isinstance(cookies_data, list):
                for cookie in cookies_data:
                    if isinstance(cookie, dict):
                        name = cookie.get("name")
                        value = cookie.get("value")
                        if name and value:
                            cookies[name] = value
            elif isinstance(cookies_data, dict):
                cookies = cookies_data

            logger.debug(f"Загружено {len(cookies)} cookies из файла")
            return cookies

        except Exception as e:
            logger.error(f"Ошибка загрузки cookies: {e}")
            return {}

    def update(self, response):
        """Обновляем cookies из ответа"""
        pass

    def handle_block(self):
        """При блокировке - ничего не делаем, т.к. cookies статичны"""
        logger.warning("Cookies заблокированы. Требуется обновить cookies вручную")
