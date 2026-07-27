from abc import ABC, abstractmethod
import requests
from loguru import logger
class Proxy(ABC):
    @abstractmethod
    def get_httpx_proxy(self) -> str | None:
        pass
    @abstractmethod
    def handle_block(self):
        pass
class NoProxy(Proxy):
    def get_httpx_proxy(self) -> str | None:
        return None
    def handle_block(self):
        pass
class ServerProxy(Proxy):
    def __init__(self, proxy: str):
        self.proxy = proxy
    def get_httpx_proxy(self) -> str | None:
        return f"http://{self.proxy}"
    def handle_block(self):
        pass
class MobileProxy(Proxy):
    def __init__(self, url: str, change_ip_url: str):
        self.url = url
        self.change_ip_url = change_ip_url
    def get_httpx_proxy(self) -> str | None:
        return f"http://{self.url}"
    def handle_block(self):
        try:
            params = {"format": "json"}
            res = requests.get(self.change_ip_url, params=params, timeout=10)
            if res.status_code == 200:
                logger.success(f"🔄 Новый IP: {res.json().get('new_ip')}")
            else:
                logger.warning(f"⚠️ Не удалось сменить IP: {res.status_code}")
        except Exception as e:
            logger.error(f"Ошибка смены IP: {e}")