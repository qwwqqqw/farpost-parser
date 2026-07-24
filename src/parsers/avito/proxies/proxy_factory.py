"""
Фабрика для создания прокси
"""
from .proxy import Proxy, NoProxy, ServerProxy, MobileProxy


def build_proxy(config) -> Proxy:
    """
    Создает объект прокси на основе конфигурации

    Args:
        config: Объект конфигурации

    Returns:
        Proxy: Объект прокси
    """
    proxy_string = getattr(config, 'proxy_string', None)
    proxy_change_url = getattr(config, 'proxy_change_url', None)

    if proxy_string and proxy_change_url:
        # Мобильный прокси с сменой IP
        return MobileProxy(url=proxy_string, change_ip_url=proxy_change_url)
    elif proxy_string:
        # Серверный прокси
        return ServerProxy(proxy=proxy_string)
    else:
        # Без прокси
        return NoProxy()
