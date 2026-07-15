"""Backfill OHLC data into database.

Usage:
    python scripts/backfill_ohlc_db.py [--symbol EURUSD] [--tf H4] [--days 30]
"""

import asyncio
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "apps/api")
sys.path.insert(0, ".")

from al_syaka_common.database import async_session_factory
from al_syaka_common.models import OHLC, Symbol
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from apps.api.src.collectors.manager import DataCollector

BATCH_SIZE = 100
CONFIG = {
    "H4": {"days": 30, "label": "~180 bars"},
    "D1": {"days": 180, "label": "~180 bars"},
}


async def backfill(symbol_filter=None, tf_filter=None):
    collector = DataCollector()
    now = datetime.now(timezone.utc)
    total = 0

    async with async_session_factory() as session:
        query = select(Symbol).where(Symbol.is_active.is_(True))
        if symbol_filter:
            query = query.where(Symbol.name == symbol_filter)
        result = await session.execute(query.order_by(Symbol.name))
        symbols = result.scalars().all()

    if not symbols:
        print("No symbols found.")
        return

    for symbol in symbols:
        for tf, cfg in CONFIG.items():
            if tf_filter and tf != tf_filter:
                continue

            start = now - timedelta(days=cfg["days"])
            msg = f"{symbol.name:<10} {tf:<5} fetching {cfg['label']}..."
            print(msg, end=" ")

            try:
                data = await collector.fetch_ohlc(
                    symbol.name, tf, start, now,
                )
                if not data:
                    print("no data")
                    continue

                # Store in its own transaction
                stored = await _store_batch(symbol.id, data, tf)
                print(f"stored {stored}/{len(data)}")
                total += stored

            except Exception as e:
                print(f"ERROR: {e}")
                continue

    print(f"\nTotal stored: {total}")


async def _store_batch(symbol_id, ohlc_list, tf):
    stored = 0
    async with async_session_factory() as session:
        for i in range(0, len(ohlc_list), BATCH_SIZE):
            batch = ohlc_list[i:i + BATCH_SIZE]
            values = []
            for o in batch:
                ts = o.timestamp
                if ts.tzinfo is not None:
                    ts = ts.replace(tzinfo=None)

                values.append({
                    "symbol_id": symbol_id,
                    "timeframe": tf,
                    "timestamp": ts,
                    "open": o.open,
                    "high": o.high,
                    "low": o.low,
                    "close": o.close,
                    "volume": o.volume or 0,
                    "spread": getattr(o, "spread", None),
                })

            stmt = (
                pg_insert(OHLC)
                .values(values)
                .on_conflict_do_nothing(
                    constraint="uq_ohlc_symbol_tf_ts",
                )
            )
            await session.execute(stmt)
            stored += len(batch)

        await session.commit()
    return stored


async def verify():
    """Check stored data after backfill."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(OHLC.timeframe, OHLC.symbol_id)
            .distinct()
        )
        tfs = set()
        for tf, sym_id in result:
            tfs.add(tf)
        print(f"Timeframes in DB: {sorted(tfs)}")

        for tf in sorted(tfs):
            result = await session.execute(
                select(OHLC.symbol_id, OHLC.timeframe,
                       func.min(OHLC.timestamp), func.max(OHLC.timestamp),
                       func.count(OHLC.timestamp))
                .where(OHLC.timeframe == tf)
                .group_by(OHLC.symbol_id, OHLC.timeframe)
                .limit(5)
            )
            for sym_id, tf_name, min_ts, max_ts, cnt in result:
                # Get symbol name
                sym = await session.get(Symbol, sym_id)
                sym_name = sym.name if sym else f"id={sym_id}"
                print(f"  {sym_name:<10} {tf_name:<5} "
                      f"{cnt:>5} bars  {min_ts.date()} - {max_ts.date()}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", help="Filter by symbol")
    parser.add_argument("--tf", help="Filter by timeframe (H4, D1)")
    parser.add_argument("--verify", action="store_true", help="Verify only")
    args = parser.parse_args()

    if args.verify:
        asyncio.run(verify())
    else:
        asyncio.run(backfill(
            symbol_filter=args.symbol,
            tf_filter=args.tf,
        ))
        print("\n--- Verification ---")
        asyncio.run(verify())
