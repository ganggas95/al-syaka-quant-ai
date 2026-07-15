"""Celery tasks for market data collection.

Periodically fetches OHLC data from external providers and
persists to the database for offline analysis, backtesting,
and macro sentiment engine.
"""

from datetime import datetime, timedelta, timezone

from al_syaka_common.database import async_session_factory
from al_syaka_common.models import OHLC, Symbol
from celery import shared_task
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

# Symbols with special timeframe handling (e.g. crypto 24/7)
CRYPTO_SYMBOLS = {"BTCUSD", "ETHUSD"}

# How far back to look for existing data per timeframe
INITIAL_BACKFILL_DAYS = {
    "H4": 30,   # ~180 bars
    "D1": 180,  # ~180 bars
}

# Batch size for database inserts
BATCH_SIZE = 100


# ──────────────────────────────────────────────
# Celery Tasks
# ──────────────────────────────────────────────

@shared_task(
    name="fetch_ohlc_h4", bind=True, max_retries=3, default_retry_delay=60,
)
def fetch_ohlc_h4_task(self):
    """Periodic task: fetch and store H4 OHLC data for all symbols."""
    import asyncio
    try:
        return asyncio.run(_fetch_and_store_ohlc(timeframe="H4"))
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(
    name="fetch_ohlc_d1", bind=True, max_retries=3, default_retry_delay=60,
)
def fetch_ohlc_d1_task(self):
    """Periodic task: fetch and store D1 OHLC data for all symbols."""
    import asyncio
    try:
        return asyncio.run(_fetch_and_store_ohlc(timeframe="D1"))
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task(name="backfill_ohlc", bind=True, max_retries=1)
def backfill_ohlc_task(self):
    """One-time task: backfill historical H4 and D1 data for all symbols.

    Run this once to populate the database before starting periodic tasks.
    """
    import asyncio
    try:
        return asyncio.run(_backfill_all_timeframes())
    except Exception as exc:
        raise self.retry(exc=exc)


# ──────────────────────────────────────────────
# Core Logic
# ──────────────────────────────────────────────

async def _fetch_and_store_ohlc(timeframe: str) -> dict:
    """Fetch OHLC data since last stored record and persist to database.

    Args:
        timeframe: 'H4' or 'D1'

    Returns:
        Summary dict with per-symbol counts.
    """
    from src.collectors.manager import DataCollector

    collector = DataCollector()
    now = datetime.now(timezone.utc)
    summary = {"timeframe": timeframe, "symbols": {}, "total_stored": 0}

    async with async_session_factory() as session:
        # Get all active symbols
        result = await session.execute(
            select(Symbol).where(Symbol.is_active.is_(True))
        )
        symbols = result.scalars().all()

        for symbol in symbols:
            try:
                # Determine data range
                start = await _get_last_timestamp(
                    session, symbol.id, timeframe, now
                )
                if start is None:
                    # No existing data — skip (backfill handles initial load)
                    msg = "skipped (no initial data)"
                    summary["symbols"][symbol.name] = msg
                    continue

                # Fetch new data
                ohlc_list = await collector.fetch_ohlc(
                    symbol.name, timeframe, start, now,
                )

                if not ohlc_list:
                    summary["symbols"][symbol.name] = "no new data"
                    continue

                # Filter out records already stored (based on start timestamp)
                new_records = [
                    o for o in ohlc_list
                    if o.timestamp > start
                ]

                if not new_records:
                    summary["symbols"][symbol.name] = "up-to-date"
                    continue

                # Store to database
                stored = await _store_batch(
                    session, symbol.id, new_records,
                )
                summary["symbols"][symbol.name] = f"stored {stored}"
                summary["total_stored"] += stored

            except Exception as e:
                err = f"error: {str(e)[:50]}"
                summary["symbols"][symbol.name] = err
                continue

        await session.commit()

    return summary


async def _backfill_all_timeframes() -> dict:
    """Backfill historical H4 and D1 data for all symbols.

    Fetches data from INITIAL_BACKFILL_DAYS ago up to now.
    """
    from src.collectors.manager import DataCollector

    collector = DataCollector()
    now = datetime.now(timezone.utc)
    summary = {"timeframes": {}}

    for timeframe, days in INITIAL_BACKFILL_DAYS.items():
        start = now - timedelta(days=days)
        tf_summary = {"symbols": {}, "total_stored": 0}

        async with async_session_factory() as session:
            result = await session.execute(
                select(Symbol).where(Symbol.is_active.is_(True))
            )
            symbols = result.scalars().all()

            for symbol in symbols:
                try:
                    # Check if data already exists
                    existing = await _get_last_timestamp(
                        session, symbol.id, timeframe, now
                    )
                    if existing and existing >= start:
                        tf_summary["symbols"][symbol.name] = "already exists"
                        continue

                    ohlc_list = await collector.fetch_ohlc(
                        symbol.name, timeframe, start, now,
                    )
                    if not ohlc_list:
                        tf_summary["symbols"][symbol.name] = "no data"
                        continue

                    stored = await _store_batch(
                        session, symbol.id, ohlc_list,
                    )
                    tf_summary["symbols"][symbol.name] = f"stored {stored}"
                    tf_summary["total_stored"] += stored

                except Exception as e:
                    err = f"error: {str(e)[:50]}"
                    tf_summary["symbols"][symbol.name] = err
                    continue

            await session.commit()

        summary["timeframes"][timeframe] = tf_summary

    return summary


# ──────────────────────────────────────────────
# Database Helpers
# ──────────────────────────────────────────────

async def _get_last_timestamp(
    session, symbol_id: int, timeframe: str, now: datetime,
) -> datetime | None:
    """Get the latest timestamp in ohlc table for this symbol+timeframe.

    Returns None if no data exists (backfill needed).
    """
    result = await session.execute(
        select(OHLC.timestamp)
        .where(
            OHLC.symbol_id == symbol_id,
            OHLC.timeframe == timeframe,
        )
        .order_by(OHLC.timestamp.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()

    if row is None:
        return None

    # For periodic tasks, start from last timestamp (exclusive).
    # Add a small overlap to avoid gaps (1 minute).
    return row - timedelta(minutes=1)


async def _store_batch(
    session, symbol_id: int, ohlc_list: list,
) -> int:
    """Upsert OHLC records into database in batches.

    Uses PostgreSQL ON CONFLICT to handle duplicates
    based on (symbol_id, timeframe, timestamp) unique constraint.
    """
    stored = 0

    for i in range(0, len(ohlc_list), BATCH_SIZE):
        batch = ohlc_list[i:i + BATCH_SIZE]

        stmt = pg_insert(OHLC).values([
            {
                "symbol_id": symbol_id,
                "timeframe": o.timeframe,
                "timestamp": o.timestamp,
                "open": o.open,
                "high": o.high,
                "low": o.low,
                "close": o.close,
                "volume": o.volume or 0,
                "spread": getattr(o, "spread", None),
            }
            for o in batch
        ])

        # Upsert: skip on conflict (already stored)
        stmt = stmt.on_conflict_do_nothing(
            constraint="uq_ohlc_symbol_tf_ts",
        )

        await session.execute(stmt)
        stored += len(batch)

    return stored
