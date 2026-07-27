class ParserError(Exception):

    pass

class NetworkError(ParserError):

    pass

class ParseHTMLError(ParserError):

    pass

class DatabaseError(Exception):

    pass

class TelegramError(Exception):

    pass

class ConfigurationError(Exception):

    pass
