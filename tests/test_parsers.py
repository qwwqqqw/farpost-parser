import pytest

from unittest.mock import Mock, patch

from src.parsers.base_parser import BaseParser

from src.parsers.farpost_parser import FarpostParser

from src.parsers.youla_parser import YoulaParser

from src.parsers.drom_parser import DromParser

class TestBaseParser:

    def test_extract_price_valid(self):

        parser = FarpostParser()

        assert parser.extract_price("10 000 ₽") == 10000.0

        assert parser.extract_price("1 500 руб") == 1500.0

        assert parser.extract_price("250000") == 250000.0

    def test_extract_price_invalid(self):

        parser = FarpostParser()

        assert parser.extract_price(None) is None

        assert parser.extract_price("") is None

        assert parser.extract_price("Договорная") is None

class TestFarpostParser:

    def test_init(self):

        parser = FarpostParser(category="tehnika", region="rossiya")

        assert parser.PLATFORM_NAME == "farpost"

        assert parser.category == "tehnika"

        assert parser.region == "rossiya"

    def test_extract_id_from_url(self):

        parser = FarpostParser()

        url = "https://www.farpost.ru/moskva/tehnika/item_1234567890"

        assert parser._extract_id_from_url(url) == "farpost_1234567890"

class TestYoulaParser:

    def test_init(self):

        parser = YoulaParser(category="electronics")

        assert parser.PLATFORM_NAME == "youla"

        assert parser.category == "electronics"

    def test_extract_id_from_url(self):

        parser = YoulaParser()

        url = "https://youla.ru/product/test-product-123abc"

        assert parser._extract_id_from_url(url) == "youla_test-product-123abc"

class TestDromParser:

    def test_init(self):

        parser = DromParser(category="electronics")

        assert parser.PLATFORM_NAME == "drom"

        assert parser.category == "electronics"

if __name__ == "__main__":

    pytest.main([__file__, "-v"])
