import sys

from pathlib import Path

from loguru import logger

from src.config import get_settings

def setup_logger():

    settings = get_settings()

    logger.remove()

    logger.add(

        sys.stdout,

        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",

        level=settings.log_level,

        colorize=True,

    )

    log_file_path = settings.base_dir / settings.log_file

    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(

        log_file_path,

        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",

        level=settings.log_level,

        rotation="10 MB",

        retention="30 days",

        compression="zip",

    )

    logger.info("Логирование настроено успешно")

    return logger
