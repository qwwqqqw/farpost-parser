from typing import Optional, List
import asyncio
import httpx
import nest_asyncio
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
from loguru import logger
from src.config import get_settings
from src.telegram.formatter import MessageFormatter
from src.utils.exceptions import TelegramError as CustomTelegramError
try:
    nest_asyncio.apply()
except:
    pass
class TelegramNotifier:
    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        settings = get_settings()
        self.token = token or settings.telegram_bot_token
        self.chat_id = chat_id or settings.telegram_chat_id
        from telegram.request import HTTPXRequest
        request = HTTPXRequest(connect_timeout=15.0, read_timeout=30.0)
        self.bot = Bot(token=self.token, request=request)
        self.formatter = MessageFormatter()
        logger.info("Telegram бот инициализирован")
    async def send_message(self, text: str, parse_mode: str = ParseMode.HTML) -> bool:
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=text,
                    parse_mode=parse_mode,
                    disable_web_page_preview=False,
                )
                logger.debug("Сообщение отправлено в Telegram")
                return True
            except TelegramError as e:
                logger.warning(f"Попытка {attempt}/{max_retries} отправки сообщения завершилась ошибкой: {e}")
                if attempt == max_retries:
                    logger.error(f"Ошибка отправки сообщения в Telegram после {max_retries} попыток: {e}")
                    raise CustomTelegramError(f"Ошибка отправки сообщения: {e}")
                await asyncio.sleep(2 * attempt)
    async def send_listing(self, listing_data: dict) -> bool:
        try:
            message = self.formatter.format_listing(listing_data)
            image_urls = listing_data.get("image_urls")
            first_image_url = None
            if image_urls:
                if isinstance(image_urls, dict):
                    first_image_url = image_urls.get("first") or image_urls.get("0")
                elif isinstance(image_urls, list) and len(image_urls) > 0:
                    first_image_url = image_urls[0]
            if first_image_url:
                try:
                    # Скачиваем изображение сами, чтобы обойти ошибку Telegram "Failed to get http url content"
                    async with httpx.AsyncClient(timeout=15.0) as client:
                        resp = await client.get(first_image_url)
                        resp.raise_for_status()
                        photo_data = resp.content

                    await self.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=photo_data,
                        caption=message,
                        parse_mode=ParseMode.HTML,
                    )
                    logger.info(f"Объявление с фото отправлено: {listing_data.get('external_id')}")
                except Exception as e:
                    logger.warning(f"Не удалось скачать или отправить фото, отправляем текст: {e}")
                    await self.send_message(message)
            else:
                await self.send_message(message)
            logger.info(f"Объявление отправлено: {listing_data.get('external_id')}")
            return True
        except Exception as e:
            logger.error(f"Ошибка отправки объявления: {e}")
            raise CustomTelegramError(f"Ошибка отправки объявления: {e}")
    async def send_statistics(self, stats: dict) -> bool:
        try:
            message = self.formatter.format_statistics(stats)
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Ошибка отправки статистики: {e}")
            return False
    async def send_error(self, error_message: str) -> bool:
        try:
            message = self.formatter.format_error(error_message)
            return await self.send_message(message)
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения об ошибке: {e}")
            return False
    async def test_connection(self) -> bool:
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"Подключение к Telegram успешно. Бот: @{bot_info.username}")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка подключения к Telegram: {e}")
            return False
    def _run_async(self, coro):
        try:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as pool:
                        future = pool.submit(asyncio.run, coro)
                        return future.result()
                else:
                    return loop.run_until_complete(coro)
            except RuntimeError:
                return asyncio.run(coro)
        except Exception as e:
            logger.error(f"Ошибка выполнения async функции: {e}")
            raise
    def send_message_sync(self, text: str) -> bool:
        try:
            return self._run_async(self.send_message(text))
        except Exception as e:
            logger.error(f"Ошибка в send_message_sync: {e}")
            return False
    def send_listing_sync(self, listing_data: dict) -> bool:
        try:
            return self._run_async(self.send_listing(listing_data))
        except Exception as e:
            logger.error(f"Ошибка в send_listing_sync: {e}")
            return False
    def send_statistics_sync(self, stats: dict) -> bool:
        try:
            return self._run_async(self.send_statistics(stats))
        except Exception as e:
            logger.error(f"Ошибка в send_statistics_sync: {e}")
            return False
    def send_error_sync(self, error_message: str) -> bool:
        try:
            return self._run_async(self.send_error(error_message))
        except Exception as e:
            logger.error(f"Ошибка в send_error_sync: {e}")
            return False
    def test_connection_sync(self) -> bool:
        try:
            return self._run_async(self.test_connection())
        except Exception as e:
            logger.error(f"Ошибка в test_connection_sync: {e}")
            return False