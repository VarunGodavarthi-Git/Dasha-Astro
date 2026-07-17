from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


from sqlalchemy import UniqueConstraint

class CachedLocation(Base):
    __tablename__ = "cached_locations"
    __table_args__ = (UniqueConstraint('query', 'country', name='uq_query_country'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    query: Mapped[str] = mapped_column(String(255), index=True)
    country: Mapped[str | None] = mapped_column(String(10), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(120))


class SavedChart(Base):
    __tablename__ = "saved_charts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_email: Mapped[str | None] = mapped_column(String(320), index=True, nullable=True)
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city_name: Mapped[str] = mapped_column(String(255), index=True)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    timezone: Mapped[str] = mapped_column(String(120))
    birth_date: Mapped[date] = mapped_column(Date)
    birth_time: Mapped[str] = mapped_column(String(16))
    chart_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_email: Mapped[str | None] = mapped_column(String(320), index=True, nullable=True)
    user_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city_name: Mapped[str] = mapped_column(String(255), index=True)
    prompt_text: Mapped[str] = mapped_column(Text)
    chart_json: Mapped[dict] = mapped_column(JSON)
    ai_response: Mapped[str] = mapped_column(Text)
    model: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
