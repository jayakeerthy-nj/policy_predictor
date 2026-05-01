from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Indicator(Base):
    __tablename__ = "indicators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str] = mapped_column(String(64), index=True)
    indicator: Mapped[str] = mapped_column(String(64), index=True)
    timestamp: Mapped[DateTime] = mapped_column(DateTime, index=True)
    value: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(64))


class NewsSignal(Base):
    __tablename__ = "news_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    headline: Mapped[str] = mapped_column(String(512))
    published_at: Mapped[DateTime] = mapped_column(DateTime, index=True)
    inflation_pressure: Mapped[float] = mapped_column(Float)
    supply_shock: Mapped[float] = mapped_column(Float)
    trade_disruption: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(64))


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    prediction_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

