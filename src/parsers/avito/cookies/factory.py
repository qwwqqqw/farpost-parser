"""
Фабрика для создания провайдеров cookies
"""
from .base import CookiesProvider
from .external_api import ExternalApiCookiesProvider
from .own_cookies import OwnCookiesProvider


def build_cookies_provider(config) -> CookiesProvider | None:
    """
    Создает провайдер cookies на основе конфигурации

    Args:
        config: Объект конфигурации

    Returns:
        CookiesProvider или None
    """
    if getattr(config, 'use_bypass_api', False) and getattr(config, 'cookies_api_key', None):
        return ExternalApiCookiesProvider(config.cookies_api_key)
    elif getattr(config, 'use_own_cookies', False):
        return OwnCookiesProvider()

    return None
