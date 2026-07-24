"""
Новый парсер для Avito, использующий API
"""
from typing import List, Dict, Optional
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs

from loguru import logger
import requests

from src.parsers.base_parser import BaseParser


class AvitoAPIParser(BaseParser):
    """Парсер для сайта Avito.ru через API"""
    
    PLATFORM_NAME = "avito"
    BASE_URL = "https://www.avito.ru"
    API_URL = "https://www.avito.ru/web/1/main/items"
    
    def __init__(self, category_id: str = "telefony", location_id: str = "ivanovo", **kwargs):
        """
        Инициализация парсера Avito
        
        Args:
            category_id: ID категории (telefony, bytovaya_elektronika, noutbuki и т.д.)
            location_id: ID региона (ivanovo, moskva и т.д.)
            **kwargs: Дополнительные параметры для BaseParser
        """
        super().__init__(**kwargs)
        self.category_id = category_id
        self.location_id = location_id
        logger.info(f"Avito API парсер инициализирован: категория={category_id}, регион={location_id}")
    
    def _get_api_headers(self):
        """Получить заголовки для API запроса"""
        headers = self._get_headers()
        headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://www.avito.ru',
            'referer': f'https://www.avito.ru/{self.location_id}/{self.category_id}',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
        })
        return headers
    
    def get_listings(self, max_pages: int = 1) -> List[Dict]:
        """
        Получить список объявлений
        
        Args:
            max_pages: Максимальное количество страниц для парсинга
            
        Returns:
            Список объявлений
        """
        listings = []
        
        try:
            # Сначала получаем страницу для извлечения параметров
            page_url = f"{self.BASE_URL}/{self.location_id}/{self.category_id}"
            logger.info(f"Загрузка страницы: {page_url}")
            
            response = self._make_request(page_url)
            
            # Извлекаем данные из JavaScript
            items_data = self._extract_items_from_html(response.text)
            
            if items_data:
                logger.info(f"Найдено {len(items_data)} объявлений через HTML")
                listings.extend(items_data)
            else:
                logger.warning("Не удалось извлечь объявления из HTML")
            
            return listings
            
        except Exception as e:
            logger.error(f"Ошибка парсинга Avito: {e}")
            import traceback
            traceback.print_exc()
            return listings
    
    def _extract_items_from_html(self, html: str) -> List[Dict]:
        """
        Извлечь объявления из HTML
        
        Args:
            html: HTML-контент страницы
            
        Returns:
            Список объявлений
        """
        listings = []
        
        try:
            # Ищем JSON данные в window.__initialData__ или __preloadedState__
            # Паттерн 1: __initialData__
            match = re.search(r'window\.__initialData__\s*=\s*({.+?});', html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    listings = self._parse_initial_data(data)
                    if listings:
                        return listings
                except Exception as e:
                    logger.debug(f"Не удалось распарсить __initialData__: {e}")
            
            # Паттерн 2: ищем JSON внутри скрипта
            pattern = r'<script[^>]*>.*?window\.__preloadedState__\s*=\s*"(.+?)".*?</script>'
            matches = re.finditer(pattern, html, re.DOTALL)
            
            for match in matches:
                try:
                    # Декодируем экранированный JSON
                    json_str = match.group(1)
                    # Убираем экранирование
                    json_str = json_str.replace('\\"', '"').replace('\\\\', '\\')
                    data = json.loads(json_str)
                    listings = self._parse_preloaded_state(data)
                    if listings:
                        return listings
                except Exception as e:
                    logger.debug(f"Не удалось распарсить __preloadedState__: {e}")
            
            # Паттерн 3: ищем структурированные данные
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'lxml')
            
            # Ищем script с type="application/ld+json"
            json_ld_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)
                    if 'itemListElement' in data:
                        listings = self._parse_json_ld(data)
                        if listings:
                            return listings
                except:
                    pass
            
            logger.warning("Не найдены данные объявлений ни в одном формате")
            
        except Exception as e:
            logger.error(f"Ошибка извлечения объявлений: {e}")
            import traceback
            traceback.print_exc()
        
        return listings
    
    def _parse_initial_data(self, data: dict) -> List[Dict]:
        """Парсинг из __initialData__"""
        listings = []
        try:
            if 'items' in data and 'items' in data['items']:
                for item in data['items']['items']:
                    listing = self._parse_item(item)
                    if listing:
                        listings.append(listing)
        except Exception as e:
            logger.debug(f"Ошибка парсинга __initialData__: {e}")
        return listings
    
    def _parse_preloaded_state(self, data: dict) -> List[Dict]:
        """Парсинг из __preloadedState__"""
        listings = []
        try:
            # Структура может быть разной, ищем массивы с items
            if 'catalog' in data and 'items' in data['catalog']:
                for item in data['catalog']['items']:
                    listing = self._parse_item(item)
                    if listing:
                        listings.append(listing)
        except Exception as e:
            logger.debug(f"Ошибка парсинга __preloadedState__: {e}")
        return listings
    
    def _parse_json_ld(self, data: dict) -> List[Dict]:
        """Парсинг из JSON-LD"""
        listings = []
        try:
            for item in data.get('itemListElement', []):
                item_data = item.get('item', {})
                listing = {
                    'platform': self.PLATFORM_NAME,
                    'external_id': f"avito_{item_data.get('sku', '')}",
                    'title': item_data.get('name', 'Без названия'),
                    'price': self.extract_price(str(item_data.get('offers', {}).get('price', ''))),
                    'url': item_data.get('url', ''),
                    'location': item_data.get('address', {}).get('addressLocality', ''),
                    'image_urls': {'first': item_data.get('image', '')},
                    'category': self.category_id,
                    'published_at': None,
                }
                if listing['external_id'] != 'avito_':
                    listings.append(listing)
        except Exception as e:
            logger.debug(f"Ошибка парсинга JSON-LD: {e}")
        return listings
    
    def _parse_item(self, item: dict) -> Optional[Dict]:
        """
        Парсинг одного объявления
        
        Args:
            item: Данные объявления из API
            
        Returns:
            Словарь с данными или None
        """
        try:
            # Извлекаем ID
            item_id = item.get('id') or item.get('itemId') or item.get('avito_id')
            if not item_id:
                return None
            
            external_id = f"avito_{item_id}"
            
            # Извлекаем заголовок
            title = item.get('title') or item.get('name') or "Без названия"
            
            # Извлекаем цену
            price = None
            if 'price' in item:
                price_data = item['price']
                if isinstance(price_data, dict):
                    price = price_data.get('value') or price_data.get('amount')
                else:
                    price = self.extract_price(str(price_data))
            
            # Извлекаем URL
            url = item.get('url') or item.get('urlPath')
            if url and not url.startswith('http'):
                url = urljoin(self.BASE_URL, url)
            
            # Извлекаем местоположение
            location = None
            if 'location' in item:
                loc_data = item['location']
                if isinstance(loc_data, dict):
                    location = loc_data.get('name') or loc_data.get('title')
                else:
                    location = str(loc_data)
            
            # Извлекаем изображение
            image_url = None
            if 'images' in item and item['images']:
                if isinstance(item['images'], list) and len(item['images']) > 0:
                    img = item['images'][0]
                    image_url = img.get('url') or img.get('src') if isinstance(img, dict) else str(img)
            elif 'image' in item:
                image_url = item['image']
            
            image_urls = {'first': image_url} if image_url else None
            
            return {
                'platform': self.PLATFORM_NAME,
                'external_id': external_id,
                'title': title,
                'price': price,
                'url': url,
                'location': location,
                'image_urls': image_urls,
                'category': self.category_id,
                'published_at': None,
            }
            
        except Exception as e:
            logger.warning(f"Ошибка парсинга объявления: {e}")
            return None
    
    def parse_listing_details(self, listing_url: str) -> Dict:
        """
        Получить детальную информацию об объявлении
        
        Args:
            listing_url: URL объявления
            
        Returns:
            Словарь с детальными данными
        """
        try:
            response = self._make_request(listing_url)
            soup = self._parse_html(response.text)
            
            # Извлекаем описание
            desc_elem = soup.select_one('[data-marker="item-description"]')
            if not desc_elem:
                desc_elem = soup.select_one('[itemprop="description"]')
            
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            return {
                'description': description,
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения деталей объявления: {e}")
            return {}
