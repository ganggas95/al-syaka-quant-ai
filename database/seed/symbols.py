"""Seed script — Insert forex symbols into database."""

import asyncio
from sqlalchemy import select
from al_syaka_common.database import async_session_factory
from al_syaka_common.models import Symbol

FOREX_SYMBOLS = [
    {"name": "EURUSD", "base": "EUR", "quote": "USD", "pip": 0.0001, "contract": 100000},
    {"name": "GBPUSD", "base": "GBP", "quote": "USD", "pip": 0.0001, "contract": 100000},
    {"name": "USDJPY", "base": "USD", "quote": "JPY", "pip": 0.01, "contract": 100000},
    {"name": "AUDUSD", "base": "AUD", "quote": "USD", "pip": 0.0001, "contract": 100000},
    {"name": "USDCAD", "base": "USD", "quote": "CAD", "pip": 0.0001, "contract": 100000},
    {"name": "NZDUSD", "base": "NZD", "quote": "USD", "pip": 0.0001, "contract": 100000},
    {"name": "EURGBP", "base": "EUR", "quote": "GBP", "pip": 0.0001, "contract": 100000},
    {"name": "EURJPY", "base": "EUR", "quote": "JPY", "pip": 0.01, "contract": 100000},
    {"name": "GBPJPY", "base": "GBP", "quote": "JPY", "pip": 0.01, "contract": 100000},
    {"name": "AUDJPY", "base": "AUD", "quote": "JPY", "pip": 0.01, "contract": 100000},
    {"name": "EURAUD", "base": "EUR", "quote": "AUD", "pip": 0.0001, "contract": 100000},
    {"name": "GBPAUD", "base": "GBP", "quote": "AUD", "pip": 0.0001, "contract": 100000},
    # Indices
    {"name": "US30", "base": "US30", "quote": "USD", "pip": 0.1, "contract": 10},
    {"name": "NAS100", "base": "NAS100", "quote": "USD", "pip": 0.1, "contract": 10},
    {"name": "SPX500", "base": "SPX500", "quote": "USD", "pip": 0.1, "contract": 10},
    # Crypto
    {"name": "BTCUSD", "base": "BTC", "quote": "USD", "pip": 0.1, "contract": 1},
    {"name": "ETHUSD", "base": "ETH", "quote": "USD", "pip": 0.01, "contract": 1},
    # Metals
    {"name": "XAUUSD", "base": "XAU", "quote": "USD", "pip": 0.01, "contract": 100},
]


async def seed_symbols():
    async with async_session_factory() as session:
        result = await session.execute(select(Symbol))
        existing = result.scalars().all()

        if existing:
            print(f"⚠️  Database already has {len(existing)} symbols. Skipping seed.")
            return

        for s in FOREX_SYMBOLS:
            symbol = Symbol(
                name=s["name"],
                base_currency=s["base"],
                quote_currency=s["quote"],
                pip_size=s["pip"],
                contract_size=s["contract"],
                is_active=True,
            )
            session.add(symbol)

        await session.commit()
        print(f"✅ Seeded {len(FOREX_SYMBOLS)} symbols into database.")


if __name__ == "__main__":
    asyncio.run(seed_symbols())
