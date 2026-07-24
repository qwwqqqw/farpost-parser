# Руководство по обновлению парсера Avito

## Что изменилось

Код парсера Avito был переработан с использованием проверенного решения из готового парсера `parser_avito`.

### Основные изменения

1. **HTTP-клиент на curl_cffi**
   - Использование `curl_cffi` вместо `httpx` для лучшего обхода защиты Cloudflare
   - Эмуляция разных браузеров (Chrome, Edge, Firefox, Safari)
   - Случайные User-Agent для каждого запроса

2. **Система управления cookies**
   - `OwnCookiesProvider` - использование собственных cookies из файла
   - `ExternalApiCookiesProvider` - покупка cookies через API (spfa.ru)
   - Автоматическое обновление cookies при блокировке

3. **Система прокси**
   - `NoProxy` - без прокси
   - `ServerProxy` - статичный серверный прокси
   - `MobileProxy` - мобильный прокси с автоматической сменой IP

4. **Обработка блокировок**
   - Отслеживание кодов 401, 403, 429
   - Счётчик попыток блокировок (`block_threshold`)
   - Автоматическая смена IP и разблокировка cookies

5. **Улучшенная фильтрация**
   - Фильтр просмотренных объявлений
   - Фильтр по цене
   - Чёрный/белый список ключевых слов
   - Фильтр по географии
   - Фильтр по продавцам
   - Фильтр по времени публикации
   - Фильтр резервов и продвинутых объявлений

6. **Парсинг JSON**
   - Точное извлечение JSON из `<script type="mime/invalid" data-mfe-state="true">`
   - Поддержка пагинации через API

## Настройка

### Переменные окружения (.env)

```env
# Основные настройки
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id

# Парсер
PARSER_INTERVAL_MINUTES=15
MAX_LISTINGS_PER_RUN=50
COUNT_PAGES=1

# Цены
MIN_PRICE=0
MAX_PRICE=999999999

# Гео
GEO=

# Время публикации (секунды, 0 = не учитывать)
MAX_AGE=0

# Паузы
PAUSE_BETWEEN_LINKS=1
MAX_COUNT_OF_RETRY=5
RETRY_DELAY=5
TIMEOUT=20
BLOCK_THRESHOLD=3

# Прокси
USE_PROXY=false
PROXY_URL=
PROXY_CHANGE_URL=

# Cookies
USE_BYPASS_API=false
COOKIES_API_KEY=
USE_OWN_COOKIES=false

# Фильтры
KEYS_WORD_WHITE_LIST=
KEYS_WORD_BLACK_LIST=
SELLER_BLACK_LIST=
IGNORE_RESERV=true
IGNORE_PROMOTION=false
```

## Использование

### Базовое использование

```python
from src.config import get_settings
from src.parsers.avito_parser_advanced import AvitoParserAdvanced

# Загрузка настроек
config = get_settings()

# Создание парсера
parser = AvitoParserAdvanced(config)

# Парсинг объявлений
listings = parser.parse("https://www.avito.ru/ivanovo/telefony")

# Получение статистики
stats = parser.get_stats()
print(stats)
```

### С использованием прокси

```python
import os
os.environ['USE_PROXY'] = 'true'
os.environ['PROXY_URL'] = 'username:password@proxy.site:port'
os.environ['PROXY_CHANGE_URL'] = 'https://changeip.mobileproxy.space/?proxy_key=***'

config = get_settings()
parser = AvitoParserAdvanced(config)
```

### С использованием собственных cookies

```python
import os
os.environ['USE_OWN_COOKIES'] = 'true'

config = get_settings()
parser = AvitoParserAdvanced(config)
# Убедитесь, что файл storage/own_cookies.json существует
```

### С использованием внешнего API для cookies

```python
import os
os.environ['USE_BYPASS_API'] = 'true'
os.environ['COOKIES_API_KEY'] = 'your_api_key_here'

config = get_settings()
parser = AvitoParserAdvanced(config)
```

## Архитектура

```
src/parsers/
├── avito/
│   ├── __init__.py
│   ├── http_client.py      # HTTP-клиент на curl_cffi
│   ├── models.py           # Модели данных (Pydantic)
│   ├── filters.py          # Фильтрация объявлений
│   ├── utils.py            # Утилиты (build_api_params, normalize_params)
│   ├── cookies/
│   │   ├── __init__.py
│   │   ├── base.py         # Абстрактный класс CookiesProvider
│   │   ├── external_api.py # Провайдер через spfa.ru API
│   │   ├── own_cookies.py  # Провайдер из файла
│   │   └── factory.py      # Фабрика провайдеров
│   └── proxies/
│       ├── __init__.py
│       ├── proxy.py        # Классы прокси
│       └── proxy_factory.py # Фабрика прокси
└── avito_parser_advanced.py # Основной парсер
```

## Тестирование

```bash
# Проверка импорта
python -c "from src.parsers.avito_parser_advanced import AvitoParserAdvanced; print('OK')"

# Проверка всех модулей
python -c "
from src.parsers.avito.http_client import HttpClient
from src.parsers.avito.proxies.proxy import NoProxy
from src.parsers.avito.cookies.factory import build_cookies_provider
from src.parsers.avito.filters import AdsFilter
print('All modules OK')
"
```

## Отличия от готового парсера

| Функция | Готовый парсер | Наш парсер |
|---------|---------------|------------|
| HTTP-клиент | curl_cffi | ✅ curl_cffi |
| Cookies провайдеры | ✅ Есть | ✅ Добавлены |
| Прокси с сменой IP | ✅ Есть | ✅ Добавлена |
| Обработка блокировок | ✅ Есть | ✅ Добавлена |
| Фильтрация объявлений | ✅ AdsFilter | ✅ AdsFilter |
| Парсинг JSON | ✅ Есть | ✅ Есть |
| API пагинация | ✅ Есть | ✅ Добавлена |
| Уведомления | ✅ Telegram/VK | ⏳ Планируется |
| Экспорт в Excel | ✅ Есть | ⏳ Планируется |
| GUI интерфейс | ✅ Flet | ⏳ Планируется |
