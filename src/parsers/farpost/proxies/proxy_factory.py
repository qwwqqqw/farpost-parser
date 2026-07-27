from .proxy import Proxy, NoProxy, ServerProxy, MobileProxy

def build_proxy(config) -> Proxy:

    proxy_string = getattr(config, 'proxy_string', None)

    proxy_change_url = getattr(config, 'proxy_change_url', None)

    if proxy_string and proxy_change_url:

        return MobileProxy(url=proxy_string, change_ip_url=proxy_change_url)

    elif proxy_string:

        return ServerProxy(proxy=proxy_string)

    else:

        return NoProxy()
