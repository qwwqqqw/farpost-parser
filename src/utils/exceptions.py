"""
Пользовательские исключения
"""


class ParserError(Exception):
    """Базовое исключение для ошибок парсера"""
    pass


class NetworkError(ParserError):
    """Ошибка сети при выполнении запроса"""
    pass


class ParseHTMLError(ParserError):
    """Ошибка при парсинге HTML"""
    pass


class DatabaseError(Exception):
    """Ошибка работы с базой данных"""
    pass


class TelegramError(Exception):
    """Ошибка отправки сообщения в Telegram"""
    pass


class ConfigurationError(Exception):
    """Ошибка конфигурации приложения"""
    pass
