"""Data Availability Assessment — Macro Sentiment Engine.

Cek ketersediaan data H4 dan D1 untuk semua simbol aktif.
Requirement minimum: 60 baris untuk trend detection yang akurat.
"""

import asyncio
import sys
from datetime import datetime, timedelta

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

sys.path.insert(0, ".")

from al_syaka_common.config import settings
from al_syaka_common.models import OHLC, Symbol


async def check_data():
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)
    session = session_factory()

    try:
        # ── 1. Cek koneksi database ──
        print("=" * 70)
        print("DATA AVAILABILITY ASSESSMENT — Macro Sentiment Engine")
        print("=" * 70)

        result = await session.execute(text("SELECT version()"))
        pg_version = result.scalar()
        print(f"\nDatabase: {pg_version.split(',')[0]}")

        # ── 2. Daftar simbol ──
        result = await session.execute(
            select(Symbol)
            .where(Symbol.is_active.is_(True))
            .order_by(Symbol.name)
        )
        symbols = result.scalars().all()
        print(f"\nTotal simbol aktif: {len(symbols)}")

        if not symbols:
            print("\n⚠️  TIDAK ADA SIMBOL AKTIF DI DATABASE!")
            print("   Macro Bias Engine tidak bisa berjalan tanpa data harga.")
            return

        # ── 3. Cek data H4 dan D1 per simbol ──
        timeframes = ["H4", "D1"]
        min_required = 60  # baris minimum untuk trend detection
        now = datetime.utcnow()

        print(f"\n{'─' * 70}")
        print(f"{'Symbol':<10} {'TF':<5} {'Rows':<8} {'Date Range':<40} {'Status':<12}")
        print(f"{'─' * 70}")

        summary = {"ok": 0, "warning": 0, "missing": 0, "total_rows": 0}

        for symbol in symbols:
            for tf in timeframes:
                result = await session.execute(
                    select(
                        func.count(OHLC.id),
                        func.min(OHLC.timestamp),
                        func.max(OHLC.timestamp),
                    ).where(
                        OHLC.symbol_id == symbol.id,
                        OHLC.timeframe == tf,
                    )
                )
                count, min_ts, max_ts = result.one()

                summary["total_rows"] += count

                if count == 0:
                    status = "❌ MISSING"
                    summary["missing"] += 1
                    date_range = "—"
                elif count < min_required:
                    status = "⚠️  LOW"
                    summary["warning"] += 1
                    date_range = f"{min_ts.strftime('%Y-%m-%d')} - {max_ts.strftime('%Y-%m-%d')}" if min_ts and max_ts else "—"
                else:
                    status = "✅ OK"
                    summary["ok"] += 1
                    date_range = f"{min_ts.strftime('%Y-%m-%d')} - {max_ts.strftime('%Y-%m-%d')}" if min_ts and max_ts else "—"

                print(f"{symbol.name:<10} {tf:<5} {count:<8} {date_range:<40} {status:<12}")

        # ── 4. Cek data freshness (apakah data H4/D1 terupdate hari ini?) ──
        print(f"\n{'─' * 70}")
        print("DATA FRESHNESS CHECK (last 7 days)")
        print(f"{'─' * 70}")

        seven_days_ago = now - timedelta(days=7)
        for symbol in symbols:
            for tf in timeframes:
                result = await session.execute(
                    select(
                        func.max(OHLC.timestamp),
                        func.count(OHLC.id),
                    ).where(
                        OHLC.symbol_id == symbol.id,
                        OHLC.timeframe == tf,
                        OHLC.timestamp >= seven_days_ago,
                    )
                )
                max_ts, recent_count = result.one()

                if max_ts:
                    hours_ago = (now - max_ts).total_seconds() / 3600
                    freshness = (
                        "RECENT" if hours_ago < 24
                        else "OLD" if hours_ago < 72
                        else "STALE"
                    )
                    print(f"  {symbol.name:<10} {tf:<5} last={max_ts.strftime('%Y-%m-%d %H:%M'):<20} "
                          f"{recent_count:<5} bars in 7d  [{freshness}]")
                else:
                    print(f"  {symbol.name:<10} {tf:<5} {'—':<20} {'—':<5} bars in 7d  [NO DATA]")

        # ── 5. Coverage untuk Macro Engine ──
        print(f"\n{'═' * 70}")
        print("MACRO ENGINE READINESS")
        print(f"{'═' * 70}")

        ready_count = 0
        for symbol in symbols:
            h4_ok = False
            d1_ok = False

            for tf in timeframes:
                result = await session.execute(
                    select(func.count(OHLC.id)).where(
                        OHLC.symbol_id == symbol.id,
                        OHLC.timeframe == tf,
                    )
                )
                count = result.scalar()
                if count >= min_required:
                    if tf == "H4":
                        h4_ok = True
                    elif tf == "D1":
                        d1_ok = True

            if h4_ok and d1_ok:
                print(f"  ✅ {symbol.name:<10} H4={h4_ok}, D1={d1_ok} → READY for Macro Engine")
                ready_count += 1
            elif h4_ok or d1_ok:
                print(f"  ⚠️  {symbol.name:<10} H4={h4_ok}, D1={d1_ok} → PARTIAL (H4/D1 fallback needed)")
            else:
                print(f"  ❌ {symbol.name:<10} H4={h4_ok}, D1={d1_ok} → NOT READY (data needed)")

        # ── 6. Summary ──
        print(f"\n{'═' * 70}")
        print(f"SUMMARY")
        print(f"{'═' * 70}")
        total_checks = len(symbols) * len(timeframes)
        print(f"  Total checks:  {total_checks}")
        print(f"  ✅ OK:         {summary['ok']}")
        print(f"  ⚠️  Low data:   {summary['warning']}")
        print(f"  ❌ Missing:    {summary['missing']}")
        print(f"  Total rows:    {summary['total_rows']:,}")
        print(f"  Symbols ready: {ready_count}/{len(symbols)}")
        print(f"\n  Minimum required bars: {min_required}")
        print(f"  Recommendation:")
        if summary["missing"] > 0:
            print(f"    ❌ MISSING data perlu dikumpulkan sebelum Macro Engine aktif.")
        if summary["warning"] > 0:
            print(f"    ⚠️  LOW data: trend detection kurang akurat (< {min_required} bars).")
        if ready_count == len(symbols):
            print(f"    ✅ SEMUA simbol READY. Macro Engine dapat diaktifkan penuh.")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("   Pastikan database PostgreSQL berjalan:")
        print("   $ docker compose up -d db  (atau sesuaikan dengan setup lokal)")
    finally:
        await session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_data())
