import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.telegram.formatter import MessageFormatter
from src.telegram.bot import TelegramNotifier
class TestMessageFormatter:
    def test_format_listing(self):
        listing_data = {
            "platform": "farpost",
            "title": "Test Listing",
            "price": 10000.0,
            "location": "Moscow",
            "category": "Electronics",
            "url": "https://example.com/listing",
        }
        message = MessageFormatter.format_listing(listing_data)
        assert "Test Listing" in message
        assert "10 000 ₽" in message
        assert "Moscow" in message
        assert "Electronics" in message
    def test_format_price(self):
        assert MessageFormatter._format_price(1000) == "1 000 ₽"
        assert MessageFormatter._format_price(10000) == "10 000 ₽"
        assert MessageFormatter._format_price(1000000) == "1 000 000 ₽"
    def test_format_statistics(self):
        stats = {
            "total": 100,
            "sent": 80,
            "unsent": 20,
            "active": 90,
        }
        message = MessageFormatter.format_statistics(stats)
        assert "100" in message
        assert "80" in message
        assert "20" in message
        assert "90" in message
class TestTelegramNotifier:
    @pytest.fixture
    def notifier(self):
        return TelegramNotifier(
            token="test_token",
            chat_id="test_chat_id"
        )
    def test_init(self, notifier):
        assert notifier.token == "test_token"
        assert notifier.chat_id == "test_chat_id"
        assert notifier.bot is not None
        assert notifier.formatter is not None
if __name__ == "__main__":
    pytest.main([__file__, "-v"])