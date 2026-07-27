from typing import Dict, Optional
from datetime import datetime
class MessageFormatter:
    @staticmethod
    def format_listing(listing_data: Dict) -> str:
        platform_emoji = {
            "farpost": "🔵",
            "youla": "🟣",
            "drom": "🟢",
        }
        platform = listing_data.get("platform", "unknown")
        emoji = platform_emoji.get(platform, "⚪")
        title = listing_data.get("title", "Без названия")
        message = f"{emoji} <b>{title}</b>\n\n"
        price = listing_data.get("price")
        if price:
            message += f"💰 <b>Цена:</b> {MessageFormatter._format_price(price)}\n"
        else:
            message += "💰 <b>Цена:</b> Не указана\n"
        location = listing_data.get("location")
        if location:
            message += f"📍 <b>Местоположение:</b> {location}\n"
        category = listing_data.get("category")
        if category:
            message += f"📂 <b>Категория:</b> {category}\n"
        published_at = listing_data.get("published_at")
        if published_at:
            if isinstance(published_at, str):
                try:
                    published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                except:
                    pass
            if isinstance(published_at, datetime):
                message += f"📅 <b>Опубликовано:</b> {published_at.strftime('%d.%m.%Y %H:%M')}\n"
        description = listing_data.get("description")
        if description:
            max_desc_length = 300
            if len(description) > max_desc_length:
                description = description[:max_desc_length] + "..."
            message += f"\n📝 <b>Описание:</b>\n{description}\n"
        url = listing_data.get("url", "")
        message += f"\n🔗 <a href='{url}'>Смотреть объявление</a>"
        message += f"\n\n<i>Платформа: {platform.upper()}</i>"
        return message
    @staticmethod
    def _format_price(price: float) -> str:
        try:
            return f"{int(price):,} ₽".replace(",", " ")
        except:
            return f"{price} ₽"
    @staticmethod
    def format_statistics(stats: Dict) -> str:
        message = "📊 <b>Статистика парсера</b>\n\n"
        message += f"📦 Всего объявлений: {stats.get('total', 0)}\n"
        message += f"✅ Отправлено: {stats.get('sent', 0)}\n"
        message += f"⏳ Ожидает отправки: {stats.get('unsent', 0)}\n"
        message += f"🔄 Активных: {stats.get('active', 0)}\n"
        return message
    @staticmethod
    def format_error(error_message: str) -> str:
        return f"❌ <b>Ошибка:</b>\n{error_message}"
    @staticmethod
    def format_success(success_message: str) -> str:
        return f"✅ <b>Успех:</b>\n{success_message}"