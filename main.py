import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from loguru import logger
from src.config import get_settings
from src.utils.logger import setup_logger
from src.database.repository import ListingRepository
from src.telegram.bot import TelegramNotifier
from src.scheduler.jobs import ParserScheduler
def main():
    parser = argparse.ArgumentParser(
        description="Парсер объявлений с отправкой в Telegram",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python main.py start              # Запустить парсер в фоновом режиме
  python main.py once               # Выполнить один раз
  python main.py stats              # Показать статистику
  python main.py test               # Проверить подключение к Telegram
        """
    )
    parser.add_argument(
        "command",
        choices=["start", "once", "stats", "test"],
        help="Команда для выполнения"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Уровень логирования (по умолчанию из .env)"
    )
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Ссылка на Farpost"
    )
    
    # Если скрипт запущен без аргументов (двойным кликом по exe), спросим команду
    if len(sys.argv) == 1:
        print("=" * 60)
        print("Добро пожаловать в парсер Farpost!")
        print("Выберите режим работы:")
        print("1. Однократный запуск (поиск новых объявлений один раз)")
        print("2. Фоновый режим (запуск 24/7 и мониторинг новых)")
        print("3. Показать статистику")
        print("=" * 60)
        choice = input("Введите номер режима (1-3): ").strip()
        if choice == "1":
            sys.argv.append("once")
        elif choice == "2":
            sys.argv.append("start")
        elif choice == "3":
            sys.argv.append("stats")
        else:
            print("[ERROR] Неверный выбор. Выход.")
            sys.exit(1)
            
    args = parser.parse_args()
    setup_logger()
    settings = get_settings()
    if args.url:
        user_input = args.url
    else:
        user_input = ""
    if args.command in ("start", "once"):
        print()
        print("=" * 60)
        if not user_input:
            user_input = input(f"Введите ссылку для поиска на Farpost: \n> ").strip()
        if user_input:
            if 'farpost.ru' in user_input.lower():
                settings.farpost_url = user_input
                settings.farpost_enabled = True
                active_url = settings.farpost_url
                print("\n[OK] Распознана ссылка Farpost")
            else:
                print("\n[ERROR] Ссылка не ведет на Farpost. Парсер остановлен.")
                print("=" * 60)
                sys.exit(1)
        else:
            print("\n[ERROR] Вы не ввели ссылку! Парсинг невозможен.")
            input("Нажмите Enter для выхода...")
            sys.exit(1)
        print(f"Используется URL: {active_url}")
        print("=" * 60)
        print()
    logger.info("=" * 60)
    logger.info("Парсер объявлений - Classifieds Site Scraper")
    logger.info("=" * 60)
    try:
        if args.command == "start":
            logger.info("Запуск планировщика в режиме 24/7")
            scheduler = ParserScheduler(settings=settings)
            scheduler.start()
        elif args.command == "once":
            logger.info("Запуск однократного парсинга")
            scheduler = ParserScheduler(settings=settings)
            scheduler.parse_and_notify_job()
            logger.info("Парсинг завершен")
        elif args.command == "stats":
            logger.info("Получение статистики")
            repository = ListingRepository()
            stats = repository.get_statistics()
            print("\n" + "=" * 60)
            print("СТАТИСТИКА ПАРСЕРА")
            print("=" * 60)
            print(f"Всего объявлений в базе:  {stats['total']}")
            print(f"Отправлено в Telegram:    {stats['sent']}")
            print(f"Ожидает отправки:         {stats['unsent']}")
            print(f"Активных объявлений:      {stats['active']}")
            print("=" * 60 + "\n")
            try:
                telegram = TelegramNotifier()
                telegram.send_statistics_sync(stats)
                logger.info("Статистика отправлена в Telegram")
            except Exception as e:
                logger.warning(f"Не удалось отправить статистику в Telegram: {e}")
        elif args.command == "test":
            logger.info("Проверка подключения к Telegram")
            telegram = TelegramNotifier()
            if telegram.test_connection_sync():
                print("\nПодключение к Telegram успешно!")
                print(f"Токен бота: {settings.telegram_bot_token[:10]}...")
                print(f"Chat ID: {settings.telegram_chat_id}\n")
                try:
                    telegram.send_message_sync("Тестовое сообщение от парсера объявлений")
                    print("Тестовое сообщение отправлено!\n")
                except Exception as e:
                    print(f"Ошибка отправки сообщения: {e}\n")
            else:
                print("\nНе удалось подключиться к Telegram")
                print("Проверьте настройки в .env файле:\n")
                print("  - TELEGRAM_BOT_TOKEN")
                print("  - TELEGRAM_CHAT_ID\n")
                sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nОстановка приложения...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)
if __name__ == "__main__":
    main()