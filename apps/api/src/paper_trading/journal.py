"""Trade Journal — Catat semua entry/exit, alasan sinyal, notes, tags."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class JournalEntry:
    """Single journal entry for a trade."""
    id: str
    position_id: str
    symbol: str
    direction: str
    entry_price: float
    exit_price: Optional[float] = None
    lot_size: float = 0.01
    profit: float = 0.0
    profit_pips: float = 0.0
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    signal: str = ""  # BUY/SELL
    confidence: float = 0.0
    reasons: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    screenshot_path: Optional[str] = None
    exit_reason: str = ""
    result: str = ""  # WIN, LOSS, BREAKEVEN
    session: str = ""  # asian, london, us
    created_at: datetime = field(default_factory=datetime.utcnow)


class TradeJournal:
    """Trade journal with notes, tags, and screenshots."""

    def __init__(self):
        self.entries: list[JournalEntry] = []
        self._next_id = 1

    def add_entry(
        self,
        position_id: str,
        symbol: str,
        direction: str,
        entry_price: float,
        lot_size: float = 0.01,
        signal: str = "",
        confidence: float = 0.0,
        reasons: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        notes: str = "",
    ) -> JournalEntry:
        """Create a new journal entry for a trade."""
        entry = JournalEntry(
            id=f"J-{self._next_id:06d}",
            position_id=position_id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            lot_size=lot_size,
            entry_time=datetime.utcnow(),
            signal=signal,
            confidence=confidence,
            reasons=reasons or [],
            tags=tags or [],
            notes=notes,
            session=self._detect_session(),
        )
        self._next_id += 1
        self.entries.append(entry)
        return entry

    def close_entry(
        self,
        position_id: str,
        exit_price: float,
        exit_reason: str = "",
        notes: str = "",
    ) -> Optional[JournalEntry]:
        """Update journal entry with exit details."""
        for entry in reversed(self.entries):
            if entry.position_id == position_id and entry.exit_price is None:
                entry.exit_price = exit_price
                entry.exit_time = datetime.utcnow()
                entry.exit_reason = exit_reason

                # Calculate result
                if entry.direction == "LONG":
                    entry.profit_pips = round((exit_price - entry.entry_price) / 0.0001, 1)
                else:
                    entry.profit_pips = round((entry.entry_price - exit_price) / 0.0001, 1)

                pip_value = 0.0001 * 100_000 * entry.lot_size
                entry.profit = round(entry.profit_pips * pip_value, 2)

                if entry.profit > 0:
                    entry.result = "WIN"
                elif entry.profit < 0:
                    entry.result = "LOSS"
                else:
                    entry.result = "BREAKEVEN"

                if notes:
                    entry.notes = notes

                return entry
        return None

    def get_entries_by_tag(self, tag: str) -> list[JournalEntry]:
        """Get all entries with a specific tag."""
        return [e for e in self.entries if tag in e.tags]

    def get_entries_by_symbol(self, symbol: str) -> list[JournalEntry]:
        """Get all entries for a symbol."""
        return [e for e in self.entries if e.symbol == symbol]

    def get_recent_entries(self, limit: int = 20) -> list[JournalEntry]:
        """Get most recent entries."""
        return sorted(self.entries, key=lambda e: e.created_at, reverse=True)[:limit]

    def _detect_session(self) -> str:
        """Detect current trading session."""
        h = datetime.utcnow().hour
        if 0 <= h < 9:
            return "asian"
        elif 8 <= h < 13:
            return "london"
        elif 13 <= h < 17:
            return "overlap"
        elif 13 <= h < 22:
            return "us"
        return "asia"
