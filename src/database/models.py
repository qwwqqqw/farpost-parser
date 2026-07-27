from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, Integer, String, Text, Float, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    pass
class Listing(Base):
    __tablename__ = "listings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    image_urls: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    region: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow,
        nullable=False
    )
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    def __repr__(self) -> str:
        return f"<Listing(id={self.id}, platform={self.platform}, external_id={self.external_id}, title={self.title[:50]})>"
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "external_id": self.external_id,
            "platform": self.platform,
            "title": self.title,
            "price": self.price,
            "description": self.description,
            "url": self.url,
            "image_urls": self.image_urls,
            "location": self.location,
            "region": self.region,
            "category": self.category,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_sent": self.is_sent,
            "is_active": self.is_active,
        }