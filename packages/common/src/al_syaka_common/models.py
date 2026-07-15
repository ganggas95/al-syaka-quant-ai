"""Core SQLAlchemy models shared across the platform."""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    BigInteger,
    Boolean,
    Text,
    Float,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from al_syaka_common.database import Base


class Symbol(Base):
    """Trading instrument metadata."""
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # e.g. EURUSD
    base_currency = Column(String(10), nullable=False)
    quote_currency = Column(String(10), nullable=False)
    exchange = Column(String(50), nullable=True)
    broker = Column(String(50), nullable=True)
    pip_size = Column(Numeric(10, 8), nullable=False, default=0.0001)
    contract_size = Column(Integer, nullable=False, default=100000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ohlc_records = relationship("OHLC", back_populates="symbol")
    ticks = relationship("Tick", back_populates="symbol")

    def __repr__(self):
        return f"<Symbol(name='{self.name}')>"


class OHLC(Base):
    """OHLC (Open, High, Low, Close) price data."""
    __tablename__ = "ohlc"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timeframe = Column(String(10), nullable=False)  # M1, M5, M15, M30, H1, H4, D1, W1, MN
    timestamp = Column(DateTime, nullable=False)
    open = Column(Numeric(12, 6), nullable=False)
    high = Column(Numeric(12, 6), nullable=False)
    low = Column(Numeric(12, 6), nullable=False)
    close = Column(Numeric(12, 6), nullable=False)
    volume = Column(BigInteger, nullable=False, default=0)
    spread = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    symbol = relationship("Symbol", back_populates="ohlc_records")

    __table_args__ = (
        UniqueConstraint("symbol_id", "timeframe", "timestamp", name="uq_ohlc_symbol_tf_ts"),
        Index("ix_ohlc_symbol_tf", "symbol_id", "timeframe"),
        Index("ix_ohlc_symbol_tf_ts", "symbol_id", "timeframe", "timestamp"),
    )

    def __repr__(self):
        return f"<OHLC(symbol_id={self.symbol_id}, tf={self.timeframe}, ts={self.timestamp})>"


class Tick(Base):
    """Tick-by-tick price data."""
    __tablename__ = "ticks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    bid = Column(Numeric(12, 6), nullable=False)
    ask = Column(Numeric(12, 6), nullable=False)
    last = Column(Numeric(12, 6), nullable=True)
    volume = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    symbol = relationship("Symbol", back_populates="ticks")

    __table_args__ = (
        Index("ix_ticks_symbol_id_ts", "symbol_id", "timestamp"),
    )

    def __repr__(self):
        return f"<Tick(symbol_id={self.symbol_id}, ts={self.timestamp})>"


class News(Base):
    """Market news and economic events."""
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(50), nullable=False)  # investing, rss, etc.
    url = Column(String(1000), nullable=True)
    published_at = Column(DateTime, nullable=False)
    impact = Column(String(10), nullable=True)  # high, medium, low
    currency = Column(String(10), nullable=True)
    category = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_news_published_at", "published_at"),
        Index("ix_news_currency", "currency"),
    )

    def __repr__(self):
        return f"<News(title='{self.title[:50]}')>"


class Signal(Base):
    """Trading signal record — stores every generated signal & its outcome."""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    signal = Column(String(10), nullable=False)  # BUY, SELL, NEUTRAL
    confidence = Column(Float, nullable=False)
    entry_price = Column(Numeric(12, 6), nullable=True)
    stop_loss = Column(Numeric(12, 6), nullable=True)
    take_profit = Column(Numeric(12, 6), nullable=True)
    risk_reward = Column(Numeric(6, 2), nullable=True)
    risk_level = Column(String(10), nullable=True)  # LOW, MEDIUM, HIGH
    reasons = Column(Text, nullable=True)  # JSON array of reasons
    indicators_used = Column(Text, nullable=True)  # JSON array
    market_trend = Column(String(20), nullable=True)  # BULLISH, BEARISH, NEUTRAL
    h1_signal = Column(String(10), nullable=True)
    h4_signal = Column(String(10), nullable=True)
    d1_signal = Column(String(10), nullable=True)
    ai_accuracy = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Outcome tracking (updated later)
    outcome_result = Column(String(10), nullable=True)  # WIN, LOSS, PENDING
    outcome_profit = Column(Numeric(12, 6), nullable=True)
    outcome_updated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_signals_symbol_created", "symbol", "created_at"),
    )

    def __repr__(self):
        return f"<Signal(symbol='{self.symbol}', signal='{self.signal}', confidence={self.confidence})>"
