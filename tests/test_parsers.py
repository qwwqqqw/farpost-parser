"""
Тесты для парсеров
"""
import pytest
from unittest.mock import Mock, patch

from src.parsers.base_parser import BaseParser
from src.parsers.avito_parser import AvitoParser
from src.parsers.youla_parser import YoulaParser
from src.parsers.drom_parser import DromParser


class TestBaseParser:
    """Тесты базового парсера"""
    
    def test_extract_price_valid(self):
        """Тест извлечения корректной цены"""
        parser = AvitoParser()
        
        assert parser.extract_price("10 000 ₽") == 10000.0
        assert parser.extract_price("1 500 руб") == 1500.0
        assert parser.extract_price("250000") == 250000.0
    
    def test_extract_price_invalid(self):
        """Тест извлечения некорректной цены"""
        parser = AvitoParser()
        
        assert parser.extract_price(None) is None
        assert parser.extract_price("") is None
        assert parser.extract_price("Договорная") is None


class TestAvitoParser:
    """Тесты парсера Avito"""
    
    def test_init(self):
        """Тест инициализации парсера"""
        parser = AvitoParser(category="tehnika", region="rossiya")
        
        assert parser.PLATFORM_NAME == "avito"
        assert parser.category == "tehnika"
        assert parser.region == "rossiya"
    
    def test_extract_id_from_url(self):
        """Тест извлечения ID из URL"""
        parser = AvitoParser()
        
        url = "https://www.avito.ru/moskva/tehnika/item_1234567890"
        assert parser._extract_id_from_url(url) == "avito_1234567890"


class TestYoulaParser:
    """Тесты парсера Youla"""
    
    def test_init(self):
        """Тест инициализации парсера"""
        parser = YoulaParser(category="electronics")
        
        assert parser.PLATFORM_NAME == "youla"
        assert parser.category == "electronics"
    
    def test_extract_id_from_url(self):
        """Тест извлечения ID из URL"""
        parser = YoulaParser()
        
        url = "https://youla.ru/product/test-product-123abc"
        assert parser._extract_id_from_url(url) == "youla_test-product-123abc"


class TestDromParser:
    """Тесты парсера Drom"""
    
    def test_init(self):
        """Тест инициализации парсера"""
        parser = DromParser(category="electronics")
        
        assert parser.PLATFORM_NAME == "drom"
        assert parser.category == "electronics"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
