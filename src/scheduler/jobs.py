"""
Планировщик задач для парсинга
"""
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
    """Планировщик задач для парсинга объявлений"""
    
    def __init__(self, settings=None):
        """Инициализация планировщика"""
        self.settings = settings if settings is not None else get_settings()
        self.scheduler = BlockingScheduler()
        self.repository = ListingRepository()
        self.telegram = TelegramNotifier()
        
        logger.info("Планировщик инициализирован")
    
    def parse_and_notify_job(self):
        """Основная задача: парсинг и отправка уведомлений"""
        try:
            logger.info("=" * 50)
            logger.info(f"Запуск задачи парсинга: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 50)
            
            # Собираем все объявления
            all_listings = []

            
            # Парсим Farpost (если включено)
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
            
            # Обрабатываем новые объявления
            new_listings_count = 0
            sent_count = 0
            
            for listing_data in all_listings[:self.settings.max_listings_per_run]:
                try:
                    # Проверяем, новое ли объявление
                    if self.repository.is_new_listing(
                        listing_data["platform"],
                        listing_data["external_id"]
                    ):
                        # Сохраняем в базу
                        saved_listing = self.repository.save_listing(listing_data)
                        new_listings_count += 1
                        
                        # Отправляем в Telegram
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
            
            # Логируем результаты
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
        """Запустить планировщик"""
        try:
            # Проверяем подключение к Telegram
            logger.info("Проверка подключения к Telegram...")
            if not self.telegram.test_connection_sync():
                logger.error("Не удалось подключиться к Telegram. Проверьте токен и chat_id")
                return
            
            # Добавляем задачу
            self.scheduler.add_job(
                self.parse_and_notify_job,
                trigger=IntervalTrigger(minutes=self.settings.parser_interval_minutes),
                id="parse_and_notify",
                name="Парсинг и отправка уведомлений",
                replace_existing=True,
            )
            
            logger.info(f"Планировщик запущен. Интервал: {self.settings.parser_interval_minutes} минут")
            logger.info("Нажмите Ctrl+C для остановки")
            
            # Запускаем задачу сразу
            logger.info("Запуск первоначальной задачи парсинга...")
            self.parse_and_notify_job()
            
            # Запускаем планировщик
            self.scheduler.start()
            
        except (KeyboardInterrupt, SystemExit):
            logger.info("Остановка планировщика...")
            self.scheduler.shutdown()
            logger.info("Планировщик остановлен")
        except Exception as e:
            logger.error(f"Ошибка запуска планировщика: {e}")
            raise
