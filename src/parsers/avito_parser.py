"""
Парсер для Avito
"""
from typing import List, Dict, Optional
from urllib.parse import urljoin
import re

from loguru import logger

from src.parsers.base_parser import BaseParser
from src.utils.exceptions import ParseHTMLError


class AvitoParser(BaseParser):
    """Парсер для сайта Avito.ru"""
    
    PLATFORM_NAME = "avito"
    BASE_URL = "https://www.avito.ru"
    
    def __init__(self, category: str = "tehnika", region: str = "rossiya", **kwargs):
        """
        Инициализация парсера Avito
        
        Args:
            category: Категория товаров
            region: Регион поиска
            **kwargs: Дополнительные параметры для BaseParser
        """
        super().__init__(**kwargs)
        self.category = category
        self.region = region
        logger.info(f"Avito парсер инициализирован: категория={category}, регион={region}")
    
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
            for page in range(1, max_pages + 1):
                logger.info(f"Парсинг страницы {page} для Avito")
                
                # Формируем URL для категории
                url = f"{self.BASE_URL}/{self.region}/{self.category}?p={page}"
                
                # Делаем запрос
                response = self._make_request(url)
                soup = self._parse_html(response.text)
                
                # Извлекаем объявления
                page_listings = self._extract_listings_from_page(soup)
                listings.extend(page_listings)
                
                logger.info(f"Найдено {len(page_listings)} объявлений на странице {page}")
                
                # Если объявлений нет, прекращаем парсинг
                if not page_listings:
                    logger.info("Объявления закончились, прекращаем парсинг")
                    break
            
            logger.info(f"Всего найдено {len(listings)} объявлений на Avito")
            return listings
            
        except Exception as e:
            logger.error(f"Ошибка парсинга Avito: {e}")
            return listings
    
    def _extract_listings_from_page(self, soup) -> List[Dict]:
        """
        Извлечь объявления со страницы
        
        Args:
            soup: BeautifulSoup объект
            
        Returns:
            Список объявлений
        """
        listings = []
        
        try:
            # Примечание: структура Avito может меняться
            # Это базовый пример селекторов, которые нужно адаптировать
            items = soup.select('[data-marker="item"]')
            
            if not items:
                logger.warning("Не найдены объявления на странице (возможно, изменилась структура)")
                return listings
            
            for item in items:
                try:
                    listing_data = self._extract_listing_data(item)
                    if listing_data:
                        listings.append(listing_data)
                except Exception as e:
                    logger.warning(f"Ошибка извлечения данных объявления: {e}")
                    continue
            
            return listings
            
        except Exception as e:
            logger.error(f"Ошибка извлечения объявлений: {e}")
            return listings
    
    def _extract_listing_data(self, item) -> Optional[Dict]:
        """
        Извлечь данные одного объявления
        
        Args:
            item: BeautifulSoup элемент объявления
            
        Returns:
            Словарь с данными или None
        """
        try:
            # Извлекаем ссылку
            link_elem = item.select_one('[data-marker="item-title"]')
            if not link_elem or not link_elem.get('href'):
                return None
            
            url = urljoin(self.BASE_URL, link_elem.get('href'))
            
            # Извлекаем ID из URL
            external_id = self._extract_id_from_url(url)
            if not external_id:
                return None
            
            # Извлекаем заголовок
            title = link_elem.get_text(strip=True) if link_elem else "Без названия"
            
            # Извлекаем цену
            price_elem = item.select_one('[data-marker="item-price"]')
            price_text = price_elem.get_text(strip=True) if price_elem else None
            price = self.extract_price(price_text)
            
            # Извлекаем местоположение
            location_elem = item.select_one('[data-marker="item-address"]')
            location = location_elem.get_text(strip=True) if location_elem else None
            
            # Извлекаем дату
            date_elem = item.select_one('[data-marker="item-date"]')
            date_text = date_elem.get_text(strip=True) if date_elem else None
            
            # Извлекаем изображение
            img_elem = item.select_one('img[src]')
            image_url = img_elem.get('src') if img_elem else None
            image_urls = {"first": image_url} if image_url else None
            
            return {
                "platform": self.PLATFORM_NAME,
                "external_id": external_id,
                "title": title,
                "price": price,
                "url": url,
                "location": location,
                "image_urls": image_urls,
                "category": self.category,
                "published_at": None,  # Avito не всегда предоставляет точную дату
            }
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения данных объявления: {e}")
            return None
    
    def _extract_id_from_url(self, url: str) -> Optional[str]:
        """
        Извлечь ID объявления из URL
        
        Args:
            url: URL объявления
            
        Returns:
            ID объявления или None
        """
        try:
            # Avito ID обычно в конце URL после последнего '_'
            match = re.search(r'_(\d+)$', url)
            if match:
                return f"avito_{match.group(1)}"
            return None
        except Exception as e:
            logger.warning(f"Ошибка извлечения ID: {e}")
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
            description = desc_elem.get_text(strip=True) if desc_elem else None
            
            return {
                "description": description,
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения деталей объявления: {e}")
            return {}
