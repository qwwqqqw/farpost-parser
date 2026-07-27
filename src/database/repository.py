from typing import List, Optional
from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from src.config import get_settings
from src.database.models import Base, Listing
from src.utils.exceptions import DatabaseError
class ListingRepository:
    def __init__(self):
        settings = get_settings()
        self.engine = create_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True,
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        logger.info("Репозиторий базы данных инициализирован")
    def get_session(self) -> Session:
        return self.SessionLocal()
    def get_by_external_id(self, platform: str, external_id: str) -> Optional[Listing]:
        try:
            with self.get_session() as session:
                stmt = select(Listing).where(
                    Listing.platform == platform,
                    Listing.external_id == external_id
                )
                result = session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Ошибка получения объявления: {e}")
            raise DatabaseError(f"Ошибка получения объявления: {e}")
    def is_new_listing(self, platform: str, external_id: str) -> bool:
        return self.get_by_external_id(platform, external_id) is None
    def save_listing(self, listing_data: dict) -> Listing:
        try:
            with self.get_session() as session:
                listing = Listing(**listing_data)
                session.add(listing)
                session.commit()
                session.refresh(listing)
                logger.info(f"Объявление сохранено: {listing.platform}:{listing.external_id}")
                return listing
        except Exception as e:
            logger.error(f"Ошибка сохранения объявления: {e}")
            raise DatabaseError(f"Ошибка сохранения объявления: {e}")
    def mark_as_sent(self, listing_id: int) -> bool:
        try:
            with self.get_session() as session:
                stmt = select(Listing).where(Listing.id == listing_id)
                result = session.execute(stmt)
                listing = result.scalar_one_or_none()
                if listing:
                    listing.is_sent = True
                    session.commit()
                    logger.info(f"Объявление {listing_id} отмечено как отправленное")
                    return True
                else:
                    logger.warning(f"Объявление {listing_id} не найдено")
                    return False
        except Exception as e:
            logger.error(f"Ошибка обновления статуса объявления: {e}")
            raise DatabaseError(f"Ошибка обновления статуса объявления: {e}")
    def get_unsent_listings(self, limit: int = 50) -> List[Listing]:
        try:
            with self.get_session() as session:
                stmt = select(Listing).where(
                    Listing.is_sent == False,
                    Listing.is_active == True
                ).limit(limit)
                result = session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Ошибка получения неотправленных объявлений: {e}")
            raise DatabaseError(f"Ошибка получения неотправленных объявлений: {e}")
    def get_statistics(self) -> dict:
        try:
            with self.get_session() as session:
                total = session.query(Listing).count()
                sent = session.query(Listing).filter(Listing.is_sent == True).count()
                unsent = session.query(Listing).filter(Listing.is_sent == False).count()
                active = session.query(Listing).filter(Listing.is_active == True).count()
                return {
                    "total": total,
                    "sent": sent,
                    "unsent": unsent,
                    "active": active,
                }
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            raise DatabaseError(f"Ошибка получения статистики: {e}")