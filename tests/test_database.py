"""
Тесты для базы данных
"""
import pytest
from datetime import datetime

from src.database.models import Listing
from src.database.repository import ListingRepository


class TestListing:
    """Тесты модели Listing"""
    
    def test_to_dict(self):
        """Тест преобразования в словарь"""
        listing = Listing(
            external_id="test_123",
            platform="avito",
            title="Test Listing",
            price=1000.0,
            url="https://example.com/listing",
        )
        
        listing_dict = listing.to_dict()
        
        assert listing_dict["external_id"] == "test_123"
        assert listing_dict["platform"] == "avito"
        assert listing_dict["title"] == "Test Listing"
        assert listing_dict["price"] == 1000.0


class TestListingRepository:
    """Тесты репозитория"""
    
    @pytest.fixture
    def repository(self):
        """Фикстура репозитория"""
        return ListingRepository()
    
    def test_save_listing(self, repository):
        """Тест сохранения объявления"""
        listing_data = {
            "external_id": f"test_{datetime.now().timestamp()}",
            "platform": "avito",
            "title": "Test Listing",
            "price": 1000.0,
            "url": "https://example.com/listing",
        }
        
        saved_listing = repository.save_listing(listing_data)
        
        assert saved_listing.id is not None
        assert saved_listing.external_id == listing_data["external_id"]
        assert saved_listing.platform == "avito"
    
    def test_is_new_listing(self, repository):
        """Тест проверки нового объявления"""
        external_id = f"test_{datetime.now().timestamp()}"
        
        # Должно быть новым
        assert repository.is_new_listing("avito", external_id) is True
        
        # Сохраняем
        listing_data = {
            "external_id": external_id,
            "platform": "avito",
            "title": "Test",
            "url": "https://example.com",
        }
        repository.save_listing(listing_data)
        
        # Теперь не должно быть новым
        assert repository.is_new_listing("avito", external_id) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
