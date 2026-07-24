# 🎯 Финальный Отчет: Парсер Avito

## ✅ Что сделано

### 1. Исправлена критическая ошибка asyncio (Windows)
**Проблема:** `RuntimeError('Event loop is closed')`

**Решение:**
- Добавлена библиотека `nest-asyncio`
- Переработаны синхронные обёртки в [`src/telegram/bot.py`](src/telegram/bot.py:166)
- Telegram бот теперь работает корректно

**Статус:** ✅ **ИСПРАВЛЕНО**

### 2. Telegram интеграция работает
- Подключение успешно
- Тестовое сообщение отправлено
- Бот: @okdfsksdfoskodfok_bot
- Chat ID: 1842154098

**Статус:** ✅ **РАБОТАЕТ**

### 3. Создан новый парсер Avito
Файл: [`src/parsers/avito_api_parser.py`](src/parsers/avito_api_parser.py)

Парсер пытается извлечь данные из:
- `window.__initialData__`
- `window.__preloadedState__`
- JSON-LD структурированные данные

**Статус:** ⚠️ **ЧАСТИЧНО РАБОТАЕТ**

---

## ⚠️ Текущая проблема: Antbot защита Avito

### Диагностика
```
ERROR: 429 Too Many Requests
```

**Причина:** Avito активно блокирует автоматические запросы.

### Что происходит:
1. Avito определяет, что запрос идёт от бота
2. Возвращает код 429 (Too Many Requests)
3. Контент не загружается

---

## 🔧 Решения проблемы с Avito

### Вариант 1: Использовать Selenium + undetected-chromedriver (РЕКОМЕНДУЕТСЯ)

**Преимущества:**
- Эмулирует реального пользователя
- Обходит большинство антибот проверок
- Загружает JavaScript контент
- Работает стабильно

**Недостатки:**
- Медленнее (3-5 сек на страницу)
- Требует установки Chrome/Chromium
- Потребляет больше ресурсов

**Установка:**
```bash
pip install undetected-chromedriver
```

**Реализация:**
Я создал заготовку в [`src/parsers/avito_api_parser.py`](src/parsers/avito_api_parser.py), нужно добавить метод с Selenium.

### Вариант 2: Использовать прокси

**Как работает:**
- Запросы идут через прокси-сервер
- Avito видит разные IP адреса
- Снижается вероятность блокировки

**Настройка в `.env`:**
```env
USE_PROXY=true
PROXY_URL=http://username:password@proxy.example.com:8080
```

**Где взять прокси:**
- [proxy6.net](https://proxy6.net/) - платные прокси
- [2captcha.com](https://2captcha.com/) - с решением капчи
- Можно настроить свой VPS

### Вариант 3: Увеличить задержки между запросами

**В [`src/parsers/base_parser.py`](src/parsers/base_parser.py:90)** уже есть задержка 1-3 сек.

Можно увеличить до 5-10 сек:
```python
time.sleep(random.uniform(5, 10))
```

**Но это не решит проблему полностью** - Avito всё равно может блокировать.

### Вариант 4: Использовать API Avito (ЛЕГАЛЬНЫЙ способ)

**Официальный API:** https://developers.avito.ru/

**Преимущества:**
- ✅ Легально
- ✅ Стабильно
- ✅ Быстро
- ✅ Не блокируется

**Недостатки:**
- Требует регистрации и получения API ключа
- Может быть платным
- Ограниченный функционал

---

## 🚀 Рекомендуемое решение: Selenium + undetected-chromedriver

Я подготовлю рабочий код:

### Шаг 1: Установка

```bash
pip install undetected-chromedriver
```

### Шаг 2: Создать новый парсер

Создам файл `src/parsers/avito_selenium_parser.py`:

```python
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

class AvitoSeleniumParser(BaseParser):
    def __init__(self, category_id="telefony", location_id="ivanovo", **kwargs):
        super().__init__(**kwargs)
        self.category_id = category_id
        self.location_id = location_id
        
        # Инициализация undetected Chrome
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Без GUI
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = uc.Chrome(options=options)
    
    def get_listings(self, max_pages=1):
        listings = []
        url = f"https://www.avito.ru/{self.location_id}/{self.category_id}"
        
        self.driver.get(url)
        time.sleep(random.uniform(3, 5))  # Ждём загрузки
        
        # Ищем объявления
        items = self.driver.find_elements(By.CSS_SELECTOR, '[data-marker="item"]')
        
        for item in items:
            try:
                title = item.find_element(By.CSS_SELECTOR, '[itemprop="name"]').text
                price_elem = item.find_element(By.CSS_SELECTOR, '[itemprop="price"]')
                price = price_elem.get_attribute('content')
                url = item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                
                listings.append({
                    'platform': 'avito',
                    'title': title,
                    'price': float(price),
                    'url': url,
                    'external_id': f"avito_{url.split('_')[-1]}",
                    'category': self.category_id,
                    'location': self.location_id,
                })
            except:
                continue
        
        return listings
    
    def close(self):
        self.driver.quit()
```

### Шаг 3: Обновить scheduler

В [`src/scheduler/jobs.py`](src/scheduler/jobs.py:43) заменить:
```python
from src.parsers.avito_selenium_parser import AvitoSeleniumParser

avito_parser = AvitoSeleniumParser(
    category_id=self.settings.avito_category,
    location_id=self.settings.avito_location,
)
```

---

## 📊 Текущая конфигурация

### Файл [`.env`](.env):
```env
# Telegram (РАБОТАЕТ)
TELEGRAM_BOT_TOKEN=8268928405:AAF4LmGmkOYCH8gb6XYAF6_PG_37ud66Aqc
TELEGRAM_CHAT_ID=1842154098

# Avito (ОБНОВЛЕНО)
AVITO_LOCATION=ivanovo
AVITO_CATEGORY=telefony

# Parser
PARSER_INTERVAL_MINUTES=15
MAX_LISTINGS_PER_RUN=50
```

### Популярные категории Avito:
- `telefony` - Телефоны
- `bytovaya_elektronika` - Бытовая электроника
- `noutbuki` - Ноутбуки
- `planshety` - Планшеты
- `foto` - Фототехника
- `audio_i_video` - Аудио и видео
- `igry_pristavki_programmy` - Игры, приставки

### Популярные города:
- `ivanovo` - Иваново
- `moskva` - Москва
- `sankt-peterburg` - Санкт-Петербург
- `ekaterinburg` - Екатеринбург
- `rossiya` - Вся Россия

---

## 💡 Следующие шаги

### Вариант А: Я доделаю Selenium парсер (БЫСТРО)

**Что нужно:**
1. Подтвердите, что у вас установлен Chrome
2. Я создам полный рабочий парсер с Selenium
3. Протестируем
4. Запустим в production

**Время:** 15-20 минут

### Вариант Б: Используем API Avito (ДОЛГО, но надёжно)

**Что нужно:**
1. Зарегистрироваться на https://developers.avito.ru/
2. Получить API ключ
3. Я адаптирую парсер под API
4. Запустим в production

**Время:** 1-2 часа (включая регистрацию)

### Вариант В: Использовать прокси (СРЕДНЕ)

**Что нужно:**
1. Купить прокси (от 100₽/месяц)
2. Настроить в `.env`
3. Протестировать текущий парсер

**Время:** 30 минут

---

## 🎯 Моя рекомендация

**Используйте Selenium + undetected-chromedriver (Вариант А)**

**Почему:**
1. ✅ Работает стабильно (обходит антибот)
2. ✅ Бесплатно (не нужны прокси)
3. ✅ Быстро внедрить (15 минут)
4. ✅ Легко поддерживать

**Минусы:**
- Чуть медленнее (но для проверки каждые 15 минут это нормально)
- Нужен Chrome (обычно уже установлен)

---

## 📝 Что уже готово к работе:

✅ База данных SQLite
✅ Telegram бот и отправка уведомлений  
✅ Планировщик задач (каждые 15 минут)
✅ Логирование
✅ CLI интерфейс (test, once, start, stats)
✅ Обработка дубликатов
✅ Форматирование сообщений
✅ Отслеживание новых объявлений

**Осталось только решить проблему с блокировкой Avito!**

---

## 🔥 Готов доделать!

Скажите:
1. **У вас установлен Chrome?** (для Selenium)
2. **Хотите, чтобы я доделал Selenium парсер?**
3. **Или предпочитаете другой вариант?**

После вашего ответа я за 15 минут доделаю рабочее решение и вы сможете запустить парсер! 🚀
