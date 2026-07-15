"""Seed script — Add XAUUSD (Gold) symbol to database."""

import asyncio
from sqlalchemy import select
from al_syaka_common.database import async_session_factory
from al_syaka_common.models import Symbol


async def add_xauusd():
    async with async_session_factory() as session:
        result = await session.execute(
            select(Symbol).where(Symbol.name == "XAUUSD")
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"✅ XAUUSD already exists in database (id={existing.id})")
            return

        symbol = Symbol(
            name="XAUUSD",
            base_currency="XAU",
            quote_currency="USD",
            pip_size=0.01,
            contract_size=100,
            is_active=True,
        )
        session.add(symbol)
        await session.commit()
        print("✅ XAUUSD (Gold) added to database!")


if __name__ == "__main__":
    asyncio.run(add_xauusd())
