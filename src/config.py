import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(..., alias="TELEGRAM_CHAT_ID")
    parser_interval_minutes: int = Field(15, alias="PARSER_INTERVAL_MINUTES")
    max_listings_per_run: int = Field(50, alias="MAX_LISTINGS_PER_RUN")
    database_url: str = Field("sqlite:///data/classifieds_parser.db", alias="DATABASE_URL")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_file: str = Field("logs/parser.log", alias="LOG_FILE")
    telegram_bot_token: Optional[str] = Field(None, alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: Optional[str] = Field(None, alias="TELEGRAM_CHAT_ID")
    farpost_url: str = Field("https://www.farpost.ru/vladivostok/auto/", alias="FARPOST_URL")
    farpost_enabled: bool = Field(True, alias="FARPOST_ENABLED")
    use_proxy: bool = Field(False, alias="USE_PROXY")
    proxy_url: Optional[str] = Field(None, alias="PROXY_URL")
    proxy_change_url: Optional[str] = Field(None, alias="PROXY_CHANGE_URL")
    use_bypass_api: bool = Field(False, alias="USE_BYPASS_API")
    cookies_api_key: Optional[str] = Field(None, alias="COOKIES_API_KEY")
    use_own_cookies: bool = Field(False, alias="USE_OWN_COOKIES")
    count_pages: int = Field(1, alias="COUNT_PAGES")
    min_price: int = Field(0, alias="MIN_PRICE")
    max_price: int = Field(999999999, alias="MAX_PRICE")
    geo: Optional[str] = Field(None, alias="GEO")
    max_age: int = Field(0, alias="MAX_AGE")
    pause_between_links: int = Field(1, alias="PAUSE_BETWEEN_LINKS")
    max_count_of_retry: int = Field(5, alias="MAX_COUNT_OF_RETRY")
    retry_delay: int = Field(5, alias="RETRY_DELAY")
    timeout: int = Field(20, alias="TIMEOUT")
    block_threshold: int = Field(3, alias="BLOCK_THRESHOLD")
    keys_word_white_list: list = Field(default_factory=list, alias="KEYS_WORD_WHITE_LIST")
    keys_word_black_list: list = Field(default_factory=list, alias="KEYS_WORD_BLACK_LIST")
    seller_black_list: list = Field(default_factory=list, alias="SELLER_BLACK_LIST")
    ignore_reserv: bool = Field(True, alias="IGNORE_RESERV")
    ignore_promotion: bool = Field(False, alias="IGNORE_PROMOTION")
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    @property
    def base_dir(self) -> Path:
        return Path(__file__).parent.parent
    @property
    def data_dir(self) -> Path:
        data_path = self.base_dir / "data"
        data_path.mkdir(exist_ok=True)
        return data_path
    @property
    def logs_dir(self) -> Path:
        logs_path = self.base_dir / "logs"
        logs_path.mkdir(exist_ok=True)
        return logs_path
def get_settings() -> Settings:
    return Settings()