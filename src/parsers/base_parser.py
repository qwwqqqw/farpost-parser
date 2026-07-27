from abc import ABC, abstractmethod

from typing import List, Dict, Optional

import time

import random

import requests

from bs4 import BeautifulSoup

from loguru import logger

from src.utils.exceptions import NetworkError, ParseHTMLError

class BaseParser(ABC):

    PLATFORM_NAME: str = "unknown"

    USER_AGENTS = [

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",

        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",

    ]

    def __init__(self, use_proxy: bool = False, proxy_url: Optional[str] = None):

        self.use_proxy = use_proxy

        self.proxy_url = proxy_url

        self.session = self._create_session()

        logger.info(f"Парсер {self.PLATFORM_NAME} инициализирован")

    def _create_session(self) -> requests.Session:

        session = requests.Session()

        session.headers.update(self._get_headers())

        if self.use_proxy and self.proxy_url:

            session.proxies = {

                "http": self.proxy_url,

                "https": self.proxy_url,

            }

        return session

    def _get_headers(self) -> dict:

        return {

            "User-Agent": random.choice(self.USER_AGENTS),

            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",

            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",

            "Accept-Encoding": "gzip, deflate, br",

            "Connection": "keep-alive",

            "Upgrade-Insecure-Requests": "1",

        }

    def _make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:

        max_retries = 3

        retry_delay = 2

        for attempt in range(max_retries):

            try:

                logger.debug(f"Запрос к {url} (попытка {attempt + 1}/{max_retries})")

                response = self.session.request(method, url, timeout=30, **kwargs)

                response.raise_for_status()

                time.sleep(random.uniform(1, 3))

                return response

            except requests.exceptions.RequestException as e:

                logger.warning(f"Ошибка запроса (попытка {attempt + 1}/{max_retries}): {e}")

                if attempt < max_retries - 1:

                    time.sleep(retry_delay * (attempt + 1))

                else:

                    raise NetworkError(f"Не удалось выполнить запрос после {max_retries} попыток: {e}")

    def _parse_html(self, html: str) -> BeautifulSoup:

        try:

            return BeautifulSoup(html, "lxml")

        except Exception as e:

            logger.error(f"Ошибка парсинга HTML: {e}")

            raise ParseHTMLError(f"Ошибка парсинга HTML: {e}")

    @abstractmethod

    def get_listings(self, **kwargs) -> List[Dict]:

        pass

    @abstractmethod

    def parse_listing_details(self, listing_url: str) -> Dict:

        pass

    def extract_price(self, price_text: Optional[str]) -> Optional[float]:

        if not price_text:

            return None

        try:

            import re

            price_clean = re.sub(r'[^\d.]', '', price_text)

            return float(price_clean) if price_clean else None

        except (ValueError, AttributeError):

            return None

    def close(self):

        if self.session:

            self.session.close()

            logger.info(f"Сессия парсера {self.PLATFORM_NAME} закрыта")
