"""
RSS парсер для Avito - самый простой и надёжный способ!
"""
from typing import List, Dict, Optional
import feedparser
import re
from datetime import datetime
from urllib.parse import urljoin, parse_qs, urlparse

from loguru import logger

from src.parsers.base_parser import BaseParser


class AvitoRSSParser(BaseParser):
    """Парсер для сайта Avito.ru через RSS"""
    
    PLATFORM_NAME = "avito"
    BASE_URL = "https://www.avito.ru"
    
    def __init__(self, category_id: str = "telefony", location_id: str = "ivanovo", **kwargs):
        """
        Инициализация парсера Avito RSS
        
        Args:
            category_id: ID категории (telefony, bytovaya_elektronika, noutbuki и т.д.)
            location_id: ID региона (ivanovo, moskva и т.д.)
            **kwargs: Дополнительные параметры для BaseParser
        """
        super().__init__(**kwargs)
        self.category_id = category_id
        self.location_id = location_id
        logger.info(f"Avito RSS парсер инициализирован: категория={category_id}, регион={location_id}")
    
    def get_listings(self, max_pages: int = 1) -> List[Dict]:
        """
        Получить список объявлений через RSS
        
        Args:
            max_pages: Игнорируется для RSS (RSS возвращает последние ~50 объявлений)
            
        Returns:
            Список объявлений
        """
        listings = []
        
        try:
            # Формируем URL RSS ленты
            # s=104 - сортировка по дате (новые сверху)
            # rss=1 - включить RSS
            rss_url = f"{self.BASE_URL}/{self.location_id}/{self.category_id}?s=104&rss=1"
            
            logger.info(f"Загрузка RSS ленты: {rss_url}")
            
            # Получаем RSS через requests (нужен User-Agent)
            response = self._make_request(rss_url)
            
            # Парсим RSS
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                logger.warning("RSS лента пуста")
                return listings
            
            logger.info(f"Найдено {len(feed.entries)} объявлений в RSS")
            
            # Обрабатываем каждое объявление
            for entry in feed.entries:
                listing = self._parse_rss_entry(entry)
                if listing:
                    listings.append(listing)
            
            logger.info(f"Успешно обработано {len(listings)} объявлений")
            return listings
            
        except Exception as e:
            logger.error(f"Ошибка парсинга Avito RSS: {e}")
            import traceback
            traceback.print_exc()
            return listings
    
    def _parse_rss_entry(self, entry) -> Optional[Dict]:
        """
        Парсинг одного объявления из RSS
        
        Args:
            entry: Элемент RSS ленты
            
        Returns:
            Словарь с данными или None
        """
        try:
            # Извлекаем заголовок
            title = entry.get('title', 'Без названия').strip()
            
            # Извлекаем ссылку
            url = entry.get('link', '')
            if not url:
                return None
            
            # Извлекаем ID из URL
            # URL формат: https://www.avito.ru/ivanovo/telefony/iphone_12_123456789
            external_id = self._extract_id_from_url(url)
            if not external_id:
                return None
            
            # Извлекаем цену
            price = None
            # В RSS могут быть разные поля для цены
            if hasattr(entry, 'avito_price'):
                price = self.extract_price(entry.avito_price)
            elif 'description' in entry:
                # Иногда цена в описании
                price_match = re.search(r'(\d[\d\s]*)\s*(?:руб|₽)', entry.description)
                if price_match:
                    price = self.extract_price(price_match.group(1))
            
            # Извлекаем описание
            description = entry.get('description', '')
            # Очищаем от HTML тегов
            description = re.sub(r'<[^>]+>', '', description).strip()
            
            # Извлекаем дату публикации
            published_at = None
            if 'published' in entry:
                try:
                    # feedparser возвращает struct_time
                    from datetime import datetime
                    published_at = datetime(*entry.published_parsed[:6])
                except:
                    pass
            
            # Извлекаем местоположение (если есть в тегах)
            location = None
            if 'tags' in entry:
                for tag in entry.tags:
                    if 'location' in tag.get('term', '').lower():
                        location = tag.get('label', '')
                        break
            
            # Если местоположение не найдено, используем location_id
            if not location:
                location = self.location_id
            
            # Извлекаем изображение (если есть)
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                image_url = entry.enclosures[0].get('href')
            
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
                'description': description[:500] if description else None,  # Ограничиваем длину
                'published_at': published_at,
            }
            
        except Exception as e:
            logger.warning(f"Ошибка парсинга RSS записи: {e}")
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
            # Пример: https://www.avito.ru/ivanovo/telefony/iphone_12_3412345678
            match = re.search(r'_(\d+)$', url)
            if match:
                return f"avito_{match.group(1)}"
            
            # Альтернативный формат
            match = re.search(r'/(\d+)$', url)
            if match:
                return f"avito_{match.group(1)}"
            
            # Если не нашли ID, используем хэш URL
            return f"avito_{abs(hash(url)) % (10 ** 10)}"
            
        except Exception as e:
            logger.warning(f"Ошибка извлечения ID: {e}")
            return None
    
    def parse_listing_details(self, listing_url: str) -> Dict:
        """
        Получить детальную информацию об объявлении
        (RSS уже содержит основную информацию)
        
        Args:
            listing_url: URL объявления
            
        Returns:
            Словарь с детальными данными
        """
        # RSS уже содержит описание, поэтому дополнительный запрос не нужен
        return {}
