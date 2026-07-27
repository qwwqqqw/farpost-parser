import os

from src.parsers.farpost_parser import FarpostParser

from src.config import Settings

class DummyConfig:

    use_proxy = False

    proxy_url = None

    timeout = 15

    max_count_of_retry = 1

    retry_delay = 1

    block_threshold = 3

parser = FarpostParser(DummyConfig())

url = "https://www.farpost.ru/vladivostok/auto/"

listings = parser.get_listings(url)

print(f"Total listings: {len(listings)}")

for i, l in enumerate(listings[:3]):

    print(f"{i+1}: {l.get('title')} - Photo: {l.get('image_urls')}")
