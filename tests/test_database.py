import pytest
from datetime import datetime
from src.database.models import Listing
from src.database.repository import ListingRepository
class TestListing:
    def test_to_dict(self):
        listing = Listing(
            external_id="test_123",
            platform="farpost",
            title="Test Listing",
            price=1000.0,
            url="https://example.com/listing",
        )
        listing_dict = listing.to_dict()
        assert listing_dict["external_id"] == "test_123"
        assert listing_dict["platform"] == "farpost"
        assert listing_dict["title"] == "Test Listing"
        assert listing_dict["price"] == 1000.0
class TestListingRepository:
    @pytest.fixture
    def repository(self):
        return ListingRepository()
    def test_save_listing(self, repository):
        listing_data = {
            "external_id": f"test_{datetime.now().timestamp()}",
            "platform": "farpost",
            "title": "Test Listing",
            "price": 1000.0,
            "url": "https://example.com/listing",
        }
        saved_listing = repository.save_listing(listing_data)
        assert saved_listing.id is not None
        assert saved_listing.external_id == listing_data["external_id"]
        assert saved_listing.platform == "farpost"
    def test_is_new_listing(self, repository):
        external_id = f"test_{datetime.now().timestamp()}"
        assert repository.is_new_listing("farpost", external_id) is True
        listing_data = {
            "external_id": external_id,
            "platform": "farpost",
            "title": "Test",
            "url": "https://example.com",
        }
        repository.save_listing(listing_data)
        assert repository.is_new_listing("farpost", external_id) is False
if __name__ == "__main__":
    pytest.main([__file__, "-v"])