from typing import List
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from src.config import get_settings
from src.database.repository import ListingRepository
from src.parsers.farpost_parser import FarpostParser
from src.telegram.bot import TelegramNotifier
class ParserScheduler:
    def __init__(self, settings=None):
        self.settings = settings if settings is not None else get_settings()
        self.scheduler = BlockingScheduler()
        self.repository = ListingRepository()
        self.telegram = TelegramNotifier()
        self._is_stopped = False
        logger.info("Планировщик инициализирован")

    def parse_and_notify_job(self):
        try:
            self._is_stopped = False
            logger.info("=" * 50)
            logger.info(f"Запуск задачи парсинга: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 50)
            all_listings = []
            if getattr(self.settings, 'farpost_enabled', False):
                try:
                    logger.info("Начинаем парсинг Farpost...")
                    farpost_parser = FarpostParser(config=self.settings)
                    farpost_url = getattr(self.settings, 'farpost_url', '')
                    if farpost_url:
                        farpost_listings = farpost_parser.get_listings(url=farpost_url)
                        all_listings.extend(farpost_listings)
                        logger.info(f"Farpost: найдено {len(farpost_listings)} объявлений")
                except Exception as e:
                    logger.error(f"Ошибка парсинга Farpost: {e}")
                    import traceback
                    traceback.print_exc()
            logger.info(f"Всего собрано {len(all_listings)} объявлений")
            new_listings_count = 0
            sent_count = 0
            for listing_data in all_listings[:self.settings.max_listings_per_run]:
                if self._is_stopped:
                    logger.warning("Процесс парсинга остановлен пользователем.")
                    break
                try:
                    if self.repository.is_new_listing(
                        listing_data["platform"],
                        listing_data["external_id"]
                    ):
                        saved_listing = self.repository.save_listing(listing_data)
                        new_listings_count += 1
                        try:
                            sent_success = self.telegram.send_listing_sync(listing_data)
                            if sent_success:
                                self.repository.mark_as_sent(saved_listing.id)
                                sent_count += 1
                                logger.info(f"Отправлено новое объявление: {listing_data['title'][:50]}")
                            else:
                                logger.warning(f"Объявление {saved_listing.id} сохранено, но не отправлено в Telegram")
                        except Exception as e:
                            logger.error(f"Ошибка отправки объявления в Telegram: {e}")
                except Exception as e:
                    logger.error(f"Ошибка обработки объявления: {e}")
            logger.info("=" * 50)
            logger.info(f"Задача завершена. Найдено: {len(all_listings)}, Новых: {new_listings_count}, Отправлено: {sent_count}")
            logger.info("=" * 50)
        except Exception as e:
            logger.error(f"Критическая ошибка в задаче парсинга: {e}")
            try:
                self.telegram.send_error_sync(f"Критическая ошибка в парсере: {str(e)}")
            except:
                pass

    def start(self):
        try:
            logger.info("Проверка подключения к Telegram...")
            if not self.telegram.test_connection_sync():
                logger.error("Не удалось подключиться к Telegram. Проверьте токен и chat_id")
                return
            self.scheduler.add_job(
                self.parse_and_notify_job,
                trigger=IntervalTrigger(minutes=self.settings.parser_interval_minutes),
                id="parse_and_notify",
                name="Парсинг и отправка уведомлений",
                replace_existing=True,
            )
            logger.info(f"Планировщик запущен. Интервал: {self.settings.parser_interval_minutes} минут")
            logger.info("Нажмите Ctrl+C для остановки")
            logger.info("Запуск первоначальной задачи парсинга...")
            self.parse_and_notify_job()
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Остановка планировщика...")
            self.scheduler.shutdown()
            logger.info("Планировщик остановлен")
        except Exception as e:
            logger.error(f"Ошибка запуска планировщика: {e}")
            raise

    def stop(self):
        try:
            self._is_stopped = True
            if self.scheduler.running:
                self.scheduler.shutdown(wait=False)
            logger.info("Парсер остановлен по команде пользователя.")
        except Exception as e:
            logger.error(f"Ошибка при остановке планировщика: {e}")