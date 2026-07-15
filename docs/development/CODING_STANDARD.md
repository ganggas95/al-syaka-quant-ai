# Standar Coding Al-Syaka Quant AI

## Struktur Monorepo

Project ini menggunakan struktur monorepo dengan package manager pnpm (untuk frontend) dan Python virtual environment (untuk backend).

```
al-syaka-quant-ai/
  apps/
    api/              # FastAPI Backend
    dashboard/        # Next.js Dashboard
    ai-engine/        # AI/ML Models
    backtester/       # Backtesting Engine
    mt5-bridge/       # MetaTrader 5 Integration
  packages/
    common/           # Shared models & config
    indicators/       # Technical indicators library
    feature-engineering/  # Feature engineering pipeline
    quant/            # Quantitative strategies
    risk/             # Risk management
  database/
    migrations/       # Alembic migrations
    seed/             # Seed data
  docker/             # Docker Compose
  docs/               # Documentation
```

Setiap package Python memiliki struktur sebagai berikut:

```
apps/api/
  src/
    al_syaka_api/     # atau nama app
      __init__.py
      module.py
  tests/
    test_module.py
  pyproject.toml
```

---

## Standar Coding Python

### 1. Type Hints

Semua fungsi dan method WAJIB menggunakan type hints Python.

```python
# Benar
def calculate_rsi(closes: list[float], period: int = 14) -> float:
    """Calculate Relative Strength Index."""
    ...

# Salah
def calculate_rsi(closes, period=14):
    ...
```

### 2. Docstrings

Gunakan Google-style docstrings untuk dokumentasi fungsi dan class.

```python
def evaluate_trade(
    signal: str,
    entry_price: float,
    confidence: float,
    atr_value: float | None = None,
) -> RiskDecision:
    """Evaluasi trade dan hitung posisi sizing.

    Args:
        signal: Arah sinyal (BUY, SELL, NEUTRAL).
        entry_price: Harga entry yang direncanakan.
        confidence: Confidence level (0.0 - 1.0).
        atr_value: Average True Range untuk SL/TP.

    Returns:
        RiskDecision dengan entry_price, stop_loss, take_profit, lot_size.

    Raises:
        ValueError: Jika entry_price <= 0 atau confidence di luar range.
    """
    ...
```

### 3. Line Length

Maksimal 79 karakter per baris (mengikuti PEP 8).

```python
# Jika melebihi 79 karakter, gunakan line continuation
total = (indicator_value_1 + indicator_value_2 + indicator_value_3
         - adjustment_factor)
```

### 4. Import Order

Urutan import (dipisah dengan baris kosong):

```python
# 1. Standard library
import asyncio
from datetime import datetime, timedelta
from typing import Optional

# 2. Third-party libraries
import pandas as pd
from fastapi import APIRouter, Query
from sqlalchemy import select

# 3. Internal modules
from al_syaka_common.database import async_session_factory
from al_syaka_common.models import Symbol
from src.collectors.manager import DataCollector
```

### 5. Naming Conventions

| Elemen | Konvensi | Contoh |
|--------|----------|--------|
| Module/File | snake_case | `market_data.py`, `signal_generator.py` |
| Class | PascalCase | `MarketStructureDetector`, `SignalGenerator` |
| Function/Method | snake_case | `calculate_rsi()`, `fetch_ohlc()` |
| Variable | snake_case | `account_balance`, `entry_price` |
| Constant | UPPER_CASE | `MAX_RETRIES = 3` |
| Private member | _prefix | `_compute_indicators()`, `_latest_values` |

### 6. Asynchronous Code

Gunakan `async/await` untuk I/O operations. Operasi CPU-bound (komputasi indikator) tetap sync.

```python
# Async untuk I/O
async def fetch_ohlc(symbol: str) -> list[OHLC]:
    async with async_session_factory() as session:
        result = await session.execute(query)
        return result.scalars().all()

# Sync untuk komputasi
def compute_indicators(df: pd.DataFrame) -> dict:
    calc = IndicatorCalculator(df)
    return calc.compute_all()
```

### 7. Error Handling

Jangan gunakan `except Exception` yang terlalu umum. Tangani exception spesifik.

```python
# Benar
try:
    data = await collector.fetch_ohlc(symbol, timeframe, start, end)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))

# Hindari (kecuali di boundary layer)
try:
    ...
except Exception:
    # Log error dan return default
    logger.exception("Unexpected error")
    return default_value
```

### 8. Logging

Gunakan `print()` hanya untuk debugging sementara. Untuk production, gunakan logging module.

```python
import logging

logger = logging.getLogger(__name__)
logger.info("Signal generated for %s: %s (confidence: %.1f%%)", symbol, signal, confidence)
```

### 9. Data Classes

Gunakan `@dataclass` untuk objek data sederhana.

```python
from dataclasses import dataclass, field

@dataclass
class SignalResult:
    symbol: str
    signal: str  # BUY, SELL, NEUTRAL
    confidence: float
    entry_price: float | None = None
    reasons: list[str] = field(default_factory=list)
```

### 10. Testing

Tulis test untuk setiap modul menggunakan pytest.

```python
# tests/test_signal_generator.py
async def test_generate_signal_buy():
    generator = SignalGenerator()
    result = await generator.generate("EURUSD", "H1")
    assert result.signal in ("BUY", "SELL", "NEUTRAL")
    assert 0 <= result.confidence <= 100
```

---

## Standar Coding TypeScript/React

### 1. TypeScript Configuration

Gunakan strict mode di `tsconfig.json`.

### 2. Naming Conventions

| Elemen | Konvensi | Contoh |
|--------|----------|--------|
| File (component) | PascalCase | `PriceChart.tsx`, `SymbolPicker.tsx` |
| File (utility) | camelCase | `api.ts`, `utils.ts` |
| Component | PascalCase | `function PriceChart()` |
| Interface/Type | PascalCase | `interface OHLCResponse` |
| Variable | camelCase | `accountBalance`, `entryPrice` |
| Function | camelCase | `fetchOhlc()`, `formatCurrency()` |

### 3. Component Structure

```tsx
// Imports
import { useState, useEffect } from "react";
import type { OHLCResponse } from "@/lib/api";

// Interface
interface PriceChartProps {
  symbol: string;
  timeframe?: string;
}

// Component
export function PriceChart({ symbol, timeframe = "H1" }: PriceChartProps) {
  const [data, setData] = useState<OHLCResponse | null>(null);

  useEffect(() => {
    fetchData();
  }, [symbol]);

  return (
    <div className="w-full h-96">
      {/* Chart implementation */}
    </div>
  );
}
```

### 4. API Calls

Semua API calls dipusatkan di `lib/api.ts`.

```typescript
// lib/api.ts
export const api = {
  ohlc: (symbol: string, timeframe = "H1", limit = 100) =>
    fetchJson<OHLCResponse>(`${API_URL}/api/v1/market/ohlc/${symbol}?timeframe=${timeframe}&limit=${limit}`),
  indicators: (symbol: string, timeframe = "H1", limit = 200) =>
    fetchJson<IndicatorsResponse>(`${API_URL}/api/v1/indicators/${symbol}?timeframe=${timeframe}&limit=${limit}`),
};
```

### 5. Styling

Gunakan Tailwind CSS dengan utility classes. Hindari CSS modules kecuali untuk komponen kompleks.

```tsx
<div className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
  <span className="text-sm text-gray-400">Symbol</span>
  <span className="text-lg font-semibold text-white">{symbol}</span>
</div>
```

### 6. State Management

Gunakan React hooks (useState, useEffect, useContext) untuk state management. Hindari Redux kecuali diperlukan.

### 7. Error Handling

```tsx
const [error, setError] = useState<string | null>(null);
const [loading, setLoading] = useState(true);

useEffect(() => {
  async function load() {
    try {
      setLoading(true);
      setError(null);
      const data = await api.ohlc(symbol);
      setData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }
  load();
}, [symbol]);
```

---

## Alat dan Tooling

### Python

| Alat | Fungsi |
|------|--------|
| black | Formatter (line length 79) |
| ruff | Linter dan import sorting |
| mypy | Static type checking |
| pytest | Testing framework |
| pytest-asyncio | Async test support |
| coverage | Code coverage |

### TypeScript/React

| Alat | Fungsi |
|------|--------|
| TypeScript | Static type checking |
| ESLint | Linter |
| Prettier | Formatter |
| Next.js | React framework |

### Git

| Alat | Fungsi |
|------|--------|
| pre-commit | Git hooks untuk linting otomatis |
| commitlint | Conventional commits |

---

## Catatan Penting

1. Jangan gunakan emoji di dalam kode atau komentar.
2. Semua teks antarmuka (UI) harus menggunakan Bahasa Inggris. Dokumentasi internal boleh Bahasa Indonesia.
3. Hindari magic numbers. Gunakan konstanta yang jelas namanya.
4. Setiap modul harus memiliki `__init__.py` yang ekspor public API.
5. Path imports: gunakan relative imports untuk modul dalam satu package, absolute imports untuk package lain.
