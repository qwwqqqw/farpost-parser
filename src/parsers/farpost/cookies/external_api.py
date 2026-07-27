import json
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
from loguru import logger
from .base import CookiesProvider
API_URL = "https://spfa.ru/api"
class ExternalApiCookiesProvider(CookiesProvider):
    MAX_STATUS_HISTORY = 20
    PURCHASE_COOLDOWN = 600  
    def __init__(self, api_key: str, storage_path: str | Path = "storage/cookies_external.json"):
        self.api_key = api_key
        self.storage_path = Path(storage_path)
        self.last_id: Optional[str] = None
        self.last_cookies: Optional[dict] = None
        self.unblock_started_at: Optional[float] = None
        self.UNBLOCK_TIMEOUT = 300  
        self.PAUSE_FOR_ERROR = 120  
        self.NOT_BALANCE = 300  
        self.WAIT_FIRST_FOR_UNBLOCK = 5  
        self.WAIT_FOR_NEW = 3  
        self.WAIT_FOR_UNBLOCK = 10  
        self.status_history: List[int] = []
        self.last_purchase_at: Optional[float] = None
        self._load_from_disk()
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
    def get(self) -> Dict[str, str]:
        if self.last_cookies:
            return self.last_cookies
        return self._get_new_cookies()
    def update(self, response):
        if not response:
            return
        code = getattr(response, "status_code", None)
        if code is None:
            return
        last_code = self.status_history[-1] if self.status_history else None
        self.status_history.append(code)
        if len(self.status_history) > self.MAX_STATUS_HISTORY:
            self.status_history.pop(0)
        if code != last_code or code in (403, 429) or last_code is None:
            self._save_to_disk()
    def handle_block(self):
        now = time.time()
        if not self.last_id:
            logger.warning("⚠️ Нет cookies id — запрашиваем новые cookies")
            self._get_new_cookies()
            return
        if self.last_purchase_at and (now - self.last_purchase_at) < self.PURCHASE_COOLDOWN:
            logger.info(f"⏱ Последняя покупка была менее 10 минут назад | id={self.last_id} | пытаемся разблокировать")
            self._try_unblock()
            return
        if (
            len(self.status_history) >= self.MAX_STATUS_HISTORY
            and all(code in (403, 429) for code in self.status_history[-self.MAX_STATUS_HISTORY:])
        ):
            logger.warning("🚨 Все последние запросы заблокированы — покупаем новые cookies")
            self._get_new_cookies()
            return
        logger.info("Пытаемся разблокировать cookies...")
        self._try_unblock()
    def _get_new_cookies(self) -> Dict[str, str]:
        try:
            logger.info("Запрашиваем новые cookies через API...")
            response = requests.post(
                f"{API_URL}/buy",
                json={"key": self.api_key},
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.last_id = data.get("id")
                self.last_cookies = data.get("cookies", {})
                self.last_purchase_at = time.time()
                if self.last_cookies:
                    logger.success(f"✅ Получены новые cookies | id={self.last_id}")
                    self._save_to_disk()
                    return self.last_cookies
                else:
                    logger.warning("⚠️ API вернул пустые cookies")
                    return {}
            elif response.status_code == 402:
                logger.error("💸 Недостаточно средств на балансе spfa.ru")
                time.sleep(self.NOT_BALANCE)
                return {}
            else:
                logger.error(f"❌ Ошибка API: {response.status_code} - {response.text}")
                time.sleep(self.PAUSE_FOR_ERROR)
                return {}
        except Exception as e:
            logger.error(f"Ошибка получения cookies: {e}")
            time.sleep(self.PAUSE_FOR_ERROR)
            return {}
    def _try_unblock(self):
        if not self.last_id:
            return
        try:
            logger.info(f"Пытаемся разблокировать cookies id={self.last_id}...")
            response = requests.post(
                f"{API_URL}/unblock",
                json={"key": self.api_key, "id": self.last_id},
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("unblocked"):
                    logger.success("✅ Cookies успешно разблокированы")
                else:
                    logger.warning("⚠️ Не удалось разблокировать cookies")
            else:
                logger.error(f"❌ Ошибка разблокировки: {response.status_code}")
        except Exception as e:
            logger.error(f"Ошибка разблокировки: {e}")
    def _load_from_disk(self):
        try:
            if self.storage_path.exists():
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_id = data.get("last_id")
                    self.last_cookies = data.get("last_cookies")
                    self.status_history = data.get("status_history", [])
                    self.last_purchase_at = data.get("last_purchase_at")
                    logger.debug(f"Загружено состояние cookies из {self.storage_path}")
        except Exception as e:
            logger.debug(f"Не удалось загрузить состояние cookies: {e}")
    def _save_to_disk(self):
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({
                    "last_id": self.last_id,
                    "last_cookies": self.last_cookies,
                    "status_history": self.status_history,
                    "last_purchase_at": self.last_purchase_at,
                }, f, indent=2)
        except Exception as e:
            logger.debug(f"Не удалось сохранить состояние cookies: {e}")