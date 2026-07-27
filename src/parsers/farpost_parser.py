from typing import List, Dict, Optional

from urllib.parse import urljoin

import re

from bs4 import BeautifulSoup

from loguru import logger

from src.parsers.base_parser import BaseParser

from src.parsers.farpost.http_client import HttpClient

from src.parsers.farpost.proxies.proxy_factory import build_proxy

class FarpostParser(BaseParser):

    PLATFORM_NAME = "farpost"

    BASE_URL = "https://www.farpost.ru"

    def __init__(self, config):

        super().__init__(

            use_proxy=getattr(config, 'use_proxy', False), 

            proxy_url=getattr(config, 'proxy_url', None)

        )

        self.config = config

        self.proxy = build_proxy(config)

        self.http_client = HttpClient(

            proxy=self.proxy,

            timeout=getattr(config, 'timeout', 20),

            max_retries=getattr(config, 'max_count_of_retry', 5),

            retry_delay=getattr(config, 'retry_delay', 5),

            block_threshold=getattr(config, 'block_threshold', 3),

        )

        logger.info(f"Farpost парсер инициализирован")

    def get_listings(self, url: str) -> List[Dict]:

        logger.info(f"Начинаем парсинг Farpost: {url}")

        listings = []

        try:

            response = self.http_client.request('GET', url)

            if not response or not response.text:

                logger.error("Не удалось получить HTML страницы Farpost")

                return listings

            html = response.content.decode('windows-1251', errors='ignore')

            if 'captcha' in html.lower() or 'подозрительный' in html.lower():

                logger.warning("Обнаружена капча или блокировка IP! Нужна смена прокси.")

            soup = BeautifulSoup(html, 'html.parser')

            items = (

                soup.select('tr.bull-item')

                or soup.select('div.bull-item')

                or soup.select('[class*="bull-item"]')

                or soup.select('a.bulletinLink')

                or soup.select('.ticket')

            )

            if not items:

                logger.warning("Не найдены объявления на странице Farpost. Возможно, капча или изменилась верстка.")

                return listings

            for item in items:

                try:

                    listing_data = self._extract_listing_data(item, url)

                    if listing_data:

                        listings.append(listing_data)

                except Exception as e:

                    logger.debug(f"Ошибка извлечения данных одного объявления: {e}")

                    continue

            logger.info(f"Найдено {len(listings)} объявлений Farpost на странице")

        except Exception as e:

            logger.error(f"Критическая ошибка парсинга Farpost: {e}")

        return listings

    def _extract_listing_data(self, item, source_url: str) -> Optional[Dict]:

        if item.name == 'a' and item.get('href'):

            title_elem = item

            container = item.find_parent('div', class_=re.compile(r'bull-item|description|subject')) or item.parent

        else:

            container = item

            title_elem = item.select_one('.bulletinLink') or item.select_one('a.title') or item.select_one('a[data-bulletin-id]')

            if not title_elem:

                title_elem = item.find('a', href=True)

        if not title_elem or not title_elem.get('href'):

            return None

        url_path = title_elem['href']

        listing_url = urljoin(self.BASE_URL, url_path)

        if not re.search(r'-\d+\.html', listing_url):

            return None

        external_id = None

        match = re.search(r'-(\d+)\.html', listing_url)

        if match:

            external_id = match.group(1)

        if not external_id:

            external_id = container.get('data-bulletin-id') or str(hash(listing_url))

        title = title_elem.text.strip()

        price = 0

        price_elem = container.select_one('.price-block__price') or container.select_one('.price') or container.find_parent('tr')

        if price_elem:

            if price_elem.select_one('.price-block__price'):

                price_text = price_elem.select_one('.price-block__price').text

            elif price_elem.select_one('.price'):

                price_text = price_elem.select_one('.price').text

            else:

                price_text = price_elem.text

            price_digits = re.sub(r'[^\d]', '', price_text)

            if price_digits:

                price = float(price_digits)

        description = None

        desc_elem = container.select_one('.annotation') or container.select_one('.description') or container.select_one('.bull-item__annotation')

        if desc_elem:

            description = desc_elem.text.strip()

        image_urls = []

        img_elem = container.select_one('img') or (item.select_one('img') if item.name != 'a' else None)

        if img_elem:

            src = img_elem.get('src') or img_elem.get('data-src')

            if src:

                if src.startswith('//'):

                    src = 'https:' + src

                elif src.startswith('/'):

                    src = urljoin(self.BASE_URL, src)

                image_urls.append(src)

        return {

            'platform': self.PLATFORM_NAME,

            'external_id': external_id,

            'title': title,

            'price': price,

            'url': listing_url,

            'description': description,

            'image_urls': image_urls,

            'location': None,

            'category': None,

            'published_at': None,

        }

    def parse_listing_details(self, listing_url: str) -> Dict:

        return {}
