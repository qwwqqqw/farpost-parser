from datetime import datetime, timedelta

from typing import Callable, List, Optional

from loguru import logger

from .models import Item

class AdsFilter:

    def __init__(self, config, is_viewed_fn: Optional[Callable] = None):

        self.config = config

        self.is_viewed_fn = is_viewed_fn

    def apply(self, ads: List[Item]) -> List[Item]:

        filters = [

            self._filter_viewed,

            self._filter_by_price_range,

            self._filter_by_black_keywords,

            self._filter_by_white_keyword,

            self._filter_by_address,

            self._filter_by_seller,

            self._filter_by_recent_time,

            self._filter_by_reserve,

            self._filter_by_promotion,

        ]

        for filter_fn in filters:

            ads = filter_fn(ads)

            logger.info(f"После фильтрации {filter_fn.__name__} осталось {len(ads)}")

            if not ads:

                return ads

        return ads

    def _filter_viewed(self, ads: List[Item]) -> List[Item]:

        if self.is_viewed_fn:

            return [ad for ad in ads if not self.is_viewed_fn(ad)]

        return ads

    def _filter_by_price_range(self, ads: List[Item]) -> List[Item]:

        min_price = getattr(self.config, 'min_price', 0)

        max_price = getattr(self.config, 'max_price', 999999999)

        if not min_price and not max_price:

            return ads

        try:

            return [ad for ad in ads if min_price <= ad.priceDetailed.value <= max_price]

        except Exception:

            return ads

    def _filter_by_black_keywords(self, ads: List[Item]) -> List[Item]:

        black_list = getattr(self.config, 'keys_word_black_list', [])

        if not black_list:

            return ads

        return [ad for ad in ads if not self._is_phrase_in_ads(ad, black_list)]

    def _filter_by_white_keyword(self, ads: List[Item]) -> List[Item]:

        white_list = getattr(self.config, 'keys_word_white_list', [])

        if not white_list:

            return ads

        return [ad for ad in ads if self._is_phrase_in_ads(ad, white_list)]

    def _filter_by_address(self, ads: List[Item]) -> List[Item]:

        geo = getattr(self.config, 'geo', None)

        if not geo:

            return ads

        return [ad for ad in ads if geo in getattr(ad, "geo", {}).get("formattedAddress", "")]

    def _filter_by_seller(self, ads: List[Item]) -> List[Item]:

        seller_black_list = getattr(self.config, 'seller_black_list', [])

        if not seller_black_list:

            return ads

        return [ad for ad in ads if not getattr(ad, "sellerId", None) or ad.sellerId not in seller_black_list]

    def _filter_by_recent_time(self, ads: List[Item]) -> List[Item]:

        max_age = getattr(self.config, 'max_age', 0)

        if not max_age:

            return ads

        now = datetime.utcnow()

        filtered = []

        for ad in ads:

            try:

                published = datetime.utcfromtimestamp(ad.sortTimeStamp / 1000)

                if (now - published) <= timedelta(seconds=max_age):

                    filtered.append(ad)

            except Exception:

                continue

        return filtered

    def _filter_by_reserve(self, ads: List[Item]) -> List[Item]:

        if not getattr(self.config, 'ignore_reserv', True):

            return ads

        return [ad for ad in ads if not getattr(ad, "isReserved", False)]

    def _filter_by_promotion(self, ads: List[Item]) -> List[Item]:

        if not getattr(self.config, 'ignore_promotion', False):

            return ads

        for ad in ads:

            ad.isPromotion = any(

                v.get("title") == "Продвинуто"

                for step in (ad.iva or {}).get("DateInfoStep", [])

                for v in step.payload.get("vas", [])

            )

        return [ad for ad in ads if not ad.isPromotion]

    @staticmethod

    def _is_phrase_in_ads(ad: Item, phrases: list) -> bool:

        full_text = ((ad.title or "") + (ad.description or "")).lower()

        return any(phrase.lower() in full_text for phrase in phrases)
