# Быстрый старт

## Шаг 1: Установка

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

## Шаг 2: Настройка Telegram бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Создайте нового бота командой `/newbot`
3. Получите токен бота
4. Получите Chat ID через [@userinfobot](https://t.me/userinfobot)

## Шаг 3: Конфигурация

```bash
# Скопируйте файл конфигурации
copy .env.example .env

# Отредактируйте .env и укажите:
# - TELEGRAM_BOT_TOKEN=ваш_токен
# - TELEGRAM_CHAT_ID=ваш_chat_id
```

## Шаг 4: Проверка

```bash
# Проверьте подключение к Telegram
python main.py test
```

## Шаг 5: Запуск

```bash
# Однократный парсинг (для теста)
python main.py once

# Запуск в режиме 24/7
python main.py start

# Просмотр статистики
python main.py stats
```

## Что дальше?

- Настройте категории и регионы в `.env`
- Настройте интервал проверки (`PARSER_INTERVAL_MINUTES`)
- Включите/отключите нужные платформы
- Настройте прокси (если требуется)

## Возможные проблемы

### Ошибка подключения к Telegram
- Проверьте токен бота
- Убедитесь, что Chat ID правильный
- Запустите `python main.py test`

### Парсер не находит объявления
- Структура сайтов может измениться
- Проверьте логи в `logs/parser.log`
- Попробуйте использовать прокси

### Ошибки зависимостей
```bash
# Обновите pip
python -m pip install --upgrade pip

# Переустановите зависимости
pip install -r requirements.txt --force-reinstall
```

---

**Готово! Ваш парсер настроен и готов к работе! 🚀**
