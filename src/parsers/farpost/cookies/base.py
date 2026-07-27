from abc import ABC, abstractmethod
from typing import Dict, Optional
import httpx
class CookiesProvider(ABC):
    @abstractmethod
    def get(self) -> Dict[str, str]:
        pass
    def update(self, response: httpx.Response) -> None:
        pass
    @abstractmethod
    def handle_block(self):
        pass