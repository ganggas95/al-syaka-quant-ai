# Development Plan — Signal Visualization Engine

## 1. Analisis Kondisi Existing vs PRD

### Existing Dashboard (`apps/dashboard/`)

**Teknologi:**
- Next.js 14 (App Router) + TypeScript
- Tailwind CSS + `tailwindcss-animate`
- Recharts, Lightweight Charts
- Lucide React icons

**Pages existing:**
| Page | Status | Keterangan |
|------|--------|------------|
| Overview (`/`) | ✅ | Stat cards, price chart, market structure summary, econ calendar |
| Market Data (`/market-data`) | ✅ | Candlestick chart, OHLC table, market movers |
| Signals (`/signals`) | ✅ | Full signal detail, composite score, macro, market structure, AI/SHAP |
| Backtesting (`/backtesting`) | ✅ | Backtest results page |
| Paper Trading (`/paper-trading`) | ✅ | Virtual trading page |
| MT5 Bridge (`/mt5`) | ✅ | MT5 connection page |
| Settings (`/settings`) | ✅ | Configuration page |

**Components existing:**
- `candle-chart.tsx`, `price-chart.tsx` — price visualization
- `mini-chart.tsx` — mini sparklines
- `econ-calendar.tsx` — economic calendar
- `market-movers.tsx` — market movers table
- `ohlc-table.tsx` — OHLC data table
- `stats-card.tsx` — stat cards
- `symbol-picker.tsx` — symbol selector
- `sidebar.tsx` — navigation
- `export-button.tsx` — export functionality

### Gap Analysis vs PRD (14 Sections)

| PRD Section | Existing | Gap |
|-------------|----------|-----|
| 1. Signal Summary | ✅ Signal banner + badges | Confidence ring, quality badge visual |
| 2. Composite Score | ✅ Breakdown cards | ⚠️ Radar chart, gauge visual |
| 3. Market Structure | ✅ Text list | ⚠️ Tree diagram, swing chart visual |
| 4. Multi Timeframe | ✅ TF boxes | ⚠️ Heatmap, alignment matrix, alignment % |
| 5. Technical Indicators | ⚠️ Text list | ❌ Mini charts, indicator gauges |
| 6. AI Explainability | ✅ SHAP text | ⚠️ Waterfall chart, force plot |
| 7. Macro Sentiment | ✅ Text cards | ⚠️ Sentiment gauge, heatmap, risk meter |
| 8. Market Regime | ✅ Text badge | ⚠️ Probability bar, regime timeline |
| 9. Entry Planning | ✅ Entry/SL/TP boxes | ⚠️ Price ladder, RR diagram |
| 10. Probability Distribution | ❌ Tidak ada | ❌ Probability bar, distribution chart |
| 11. Risk Analysis | ⚠️ Risk badge | ❌ Risk gauge, risk matrix |
| 12. Historical Performance | ❌ Tidak ada | ❌ Equity curve, monthly heatmap |
| 13. Trade Timeline | ❌ Tidak ada | ❌ Timeline chart, candle overlay |
| 14. AI Decision Flow | ❌ Tidak ada | ❌ Flow diagram, decision tree |

**Legend:** ✅ Done / ⚠️ Partial / ❌ Missing

### Gap Analysis — Interactive Features

| Feature | Status |
|---------|--------|
| Hover tooltip | ⚠️ Basic (Next.js default) |
| Zoom | ❌ |
| Timeframe Switch | ✅ (di signals page) |
| History Replay | ❌ |
| Explain Mode | ❌ |
| Dark Mode | ✅ (via Tailwind dark theme) |
| Export (PNG/PDF/JSON) | ⚠️ Basic export button |

### Gap Analysis — API Endpoints

| Endpoint | Status |
|----------|--------|
| `GET /signal/{id}` | ⚠️ Via unified-signal (realtime) |
| `GET /signal/history` | ❌ |
| `GET /signal/composite` | ❌ |
| `GET /signal/shap` | ❌ |
| `GET /signal/performance` | ❌ |
| `GET /signal/market-structure` | ✅ (via market-structure router) |
| `GET /signal/macro` | ❌ |

---

## 2. Arsitektur Usulan

### Component Tree

```
dashboard/
├── src/
│   ├── app/
│   │   ├── signals/           ← Enhanced (existing)
│   │   ├── visualization/     ← NEW: Dashboard visualisasi penuh
│   │   │   ├── composite/     ← Radar chart + breakdown
│   │   │   ├── macro/         ← Sentiment gauge
│   │   │   ├── regime/        ← Regime probability bar
│   │   │   ├── shap/          ← Waterfall chart
│   │   │   ├── performance/   ← Equity curve
│   │   │   └── timeline/      ← Trade timeline
│   │   └── replay/            ← NEW: History replay
│   ├── components/
│   │   ├── charts/            ← NEW: Chart components
│   │   │   ├── radar-chart.tsx
│   │   │   ├── gauge-chart.tsx
│   │   │   ├── waterfall-chart.tsx
│   │   │   ├── heatmap-chart.tsx
│   │   │   ├── equity-curve.tsx
│   │   │   ├── probability-bar.tsx
│   │   │   ├── alignment-matrix.tsx
│   │   │   ├── regime-timeline.tsx
│   │   │   └── decision-flow.tsx
│   │   ├── signal/            ← NEW: Signal-specific
│   │   │   ├── confidence-ring.tsx
│   │   │   ├── quality-badge.tsx
│   │   │   ├── risk-meter.tsx
│   │   │   ├── entry-ladder.tsx
│   │   │   └── rr-diagram.tsx
│   │   └── shared/            ← Existing + enhanced
│   │       ├── tooltip.tsx
│   │       ├── loading-skeleton.tsx
│   │       └── export-button.tsx
│   └── lib/
│       └── api-visualization.ts  ← NEW: API client untuk V2
```

### API Endpoints Baru (Backend)

```
GET  /api/v2/signal/{id}/composite     → Composite breakdown + radar data
GET  /api/v2/signal/{id}/shap          → SHAP waterfall data
GET  /api/v2/signal/{id}/macro         → Macro sentiment detail
GET  /api/v2/signal/{id}/regime        → Regime probability
GET  /api/v2/signal/{id}/entry         → Entry planning detail
GET  /api/v2/signal/history            → Historical signals
GET  /api/v2/signal/performance        → Equity curve, metrics
GET  /api/v2/signal/timeline           → Trade timeline
WS   /api/v2/signal/realtime           → WebSocket real-time update
```

---

## 3. Milestone & Sprint Plan

### Phase 1 — Static Visualization (Sprint 1-2)
**Tujuan:** All 14 sections rendered with static data + mock charts.

#### Sprint 1.1 — Composite & Macro Visualization
**Task 1.1.1** — Radar Chart untuk Composite Score
- Buat `radar-chart.tsx` component using Recharts
- 5 axes: Market Structure, Momentum, Trend, Volatility, AI Prediction
- Color-coded per axis

**Task 1.1.2** — Gauge Chart untuk Macro Sentiment
- Buat `gauge-chart.tsx` component
- Needle-style gauge: BULLISH (green), BEARISH (red), NEUTRAL (gray)
- Confidence percentage display

**Task 1.1.3** — Confidence Ring untuk Signal Summary
- Buat `confidence-ring.tsx` (SVG circle animation)
- Color transitions: < 40 red, 40-70 yellow, > 70 green

**Task 1.1.4** — Quality & Risk Badges
- Buat `quality-badge.tsx`, `risk-meter.tsx`
- Visual: color-coded chips with icon

**Task 1.1.5** — Integrasi ke halaman Signals
- Update `signals/page.tsx` — replace text cards with chart components
- Data binding from existing API response

**Deliverable:** Signals page dengan radar, gauge, confidence ring

#### Sprint 1.2 — Market Structure & Regime
**Task 1.2.1** — Market Structure Tree Diagram
- Buat `market-structure-tree.tsx`
- Tree: Trend → Swing → BOS → CHOCH → FVG → Liquidity

**Task 1.2.2** — Multi Timeframe Alignment Matrix
- Buat `alignment-matrix.tsx`
- Heatmap-style: M15, H1, H4, D1 with BUY/SELL/NEUTRAL colors
- Alignment percentage calculation

**Task 1.2.3** — Regime Probability Bar
- Buat `regime-probability.tsx`
- Horizontal stacked bar: Trending, Range, High Volatility, etc.

**Task 1.2.4** — Technical Indicator Gauges
- Buat `indicator-gauges.tsx`
- Mini gauge per indicator: RSI (0-100), ADX (0-100), MACD (+/-)

**Deliverable:** Structure, regime, indicators visualization

---

### Phase 2 — Interactive Dashboard (Sprint 3-4)
**Tujuan:** Interactive controls, filtering, timeframe switching, hover details.

#### Sprint 2.1 — Interactive Controls
**Task 2.1.1** — Timeline Range Selector
- Date range picker: 1D, 1W, 1M, 3M, 1Y, custom
- Connected to all chart components

**Task 2.1.2** — Symbol Auto-Complete
- Update `symbol-picker.tsx` with search + categories (INDICES, FOREX, CRYPTO, METALS)

**Task 2.1.3** — Hover Tooltip System
- Unified tooltip component with dark theme styling
- Show exact values, percentages, explanations on hover

**Task 2.1.4** — Export Enhanced
- Export PNG (using html-to-image), PDF, JSON
- Styled export with header/timestamp

#### Sprint 2.2 — Real-time Updates
**Task 2.2.1** — WebSocket Connection
- New `lib/websocket.ts` client
- Auto-reconnect with exponential backoff
- Connection status indicator

**Task 2.2.2** — Live Price Updates
- Update `price-chart.tsx` for real-time candle updates
- Auto-scroll to latest candle

**Task 2.2.3** — Live Signal Updates
- Push notification when new signal generated
- Badge counter on sidebar

**Task 2.2.4** — Loading Skeleton
- `loading-skeleton.tsx` for each chart component
- Animated pulse placeholders

**Deliverable:** Fully interactive dashboard with real-time updates

---

### Phase 3 — Historical Replay (Sprint 5)
**Tujuan:** Replay historical signals with candle overlay.

**Task 3.1.1** — Backend: Signal History API
- `GET /api/v2/signal/history` with pagination
- Filter by symbol, timeframe, date range, decision type

**Task 3.1.2** — Trade Timeline Component
- Horizontal timeline with signal markers
- Color-coded: BUY (green), SELL (red), HEDGE (purple), WAIT (yellow)
- Click to expand details

**Task 3.1.3** — Candle Overlay
- Lightweight Charts integration
- Overlay signal markers on candlestick chart
- Entry/SL/TP levels as horizontal lines

**Task 3.1.4** — Playback Controls
- Play, pause, speed control (1x, 2x, 5x, 10x)
- Timeline scrubber

**Deliverable:** Historical signal replay with trade visualization

---

### Phase 4 — Backtesting Visualization (Sprint 6)
**Tujuan:** Visualize backtest results from `apps/backtester/`.

**Task 4.1.1** — Backend: Performance Metrics API
- `GET /api/v2/signal/performance`
- Equity curve, drawdown, win rate, profit factor, Sharpe ratio

**Task 4.1.2** — Equity Curve Component
- `equity-curve.tsx` (Recharts AreaChart)
- With drawdown overlay (red area below)
- Trade markers on curve

**Task 4.1.3** — Monthly Returns Heatmap
- Calendar-style heatmap
- Green/red cells for monthly PnL

**Task 4.1.4** — Performance Stats Cards
- Win Rate, Profit Factor, Expectancy, Sharpe, Max Drawdown, Recovery Factor
- Visual indicators: ▲▼ for improvement/decline

**Task 4.1.5** — Strategy Comparison
- Compare multiple strategies side by side
- Overlay equity curves

**Deliverable:** Backtesting analytics dashboard with performance metrics

---

### Phase 5 — Portfolio Visualization (Sprint 7)
**Tujuan:** Multi-symbol portfolio view.

**Task 5.1.1** — Portfolio Summary
- Total PnL, total positions, win rate, exposure
- Pie chart: symbol allocation by capital

**Task 5.1.2** — Correlation Matrix
- Heatmap of symbol correlations
- Pair-wise return correlation

**Task 5.1.3** — Risk Contribution
- Treemap: risk contribution per symbol
- Color intensity = risk level

**Deliverable:** Portfolio-level analytics dashboard

---

### Phase 6 — AI Explainability Dashboard (Sprint 8)
**Tujuan:** Interactive SHAP visualization.

**Task 6.1.1** — Backend: SHAP Detail API
- `GET /api/v2/signal/{id}/shap`
- Feature name, SHAP value, base value, predicted value

**Task 6.1.2** — Waterfall Chart
- `waterfall-chart.tsx` (custom SVG implementation)
- Base value → feature contributions → final prediction
- Color: red (negative impact), green (positive impact)

**Task 6.1.3** — SHAP Force Plot
- Simplified force plot visualization
- Features pushing left (SELL) vs right (BUY)

**Task 6.1.4** — Feature Importance Bar
- Horizontal bar chart sorted by |SHAP value|
- With direction indicator

**Task 6.1.5** — Explain Mode
- Toggle between "summary" and "detailed" view
- Click feature to see how it was calculated

**Deliverable:** AI explainability dashboard with interactive SHAP visualization

---

### Phase 7 — Institutional Analytics (Sprint 9)
**Tujuan:** Advanced analytics for institutional users.

**Task 7.1.1** — Risk Matrix
- Multi-dimensional risk view
- Greeks, VaR, stress testing visualization

**Task 7.1.2** — Decision Flow Diagram
- Sankey/flow diagram showing pipeline stages
- AI → Composite → Macro → Risk → Final Decision

**Task 7.1.3** — Probability Distribution
- Bell curve / distribution chart
- Confidence intervals

**Task 7.1.4** — Entry Planning Ladder
- Price ladder: entry, SL, TP levels with ATR bands
- Risk/Reward ratio visualization

**Deliverable:** Institutional-grade analytics dashboard

---

## 4. Timeline & Dependencies

```
Phase 1: Static Visualization ───────────────── Sprint 1-2 (2 weeks)
  ├── Sprint 1.1: Composite & Macro ── 1 week
  ├── Sprint 1.2: Structure & Regime ── 1 week
  │
Phase 2: Interactive Dashboard ──────────────── Sprint 3-4 (2 weeks)
  ├── Sprint 2.1: Interactive Controls ── 1 week
  ├── Sprint 2.2: Real-time Updates ──── 1 week
  │
Phase 3: Historical Replay ──────────────────── Sprint 5 (1 week)
Phase 4: Backtesting Visualization ──────────── Sprint 6 (1 week)
Phase 5: Portfolio Visualization ────────────── Sprint 7 (1 week)
Phase 6: AI Explainability Dashboard ────────── Sprint 8 (1 week)
Phase 7: Institutional Analytics ────────────── Sprint 9 (1 week)
```

**Critical Path:** Phase 1 → Phase 2 → Phase 3 → Phase 4
**Parallelizable:** Phase 5, 6, 7 (dapat dikerjakan paralel setelah Phase 2)

---

## 5. Teknologi Spesifik

| Kebutuhan | Pilihan | Alasan |
|-----------|---------|--------|
| Radar Chart | Recharts | Already in project |
| Gauge | Custom SVG | Lightweight, no extra dep |
| Waterfall | Custom SVG | Recharts tidak punya waterfall |
| Heatmap | Recharts | Already in project |
| Equity Curve | Recharts AreaChart | Already in project |
| Candlestick | Lightweight Charts | Already in project |
| Flow Diagram | Custom SVG/CSS | Sankey too heavy for this |
| Timeline | Recharts/Custom | Depend on complexity |
| Tree Diagram | Custom CSS | Simple tree, no dep needed |
| Tooltip | Custom + Radix | Already using Radix |
| WebSocket | Native WebSocket | No extra dep needed |
| Export | html-to-image | Standard approach |
| Animations | Tailwind + Framer Motion | If needed for complex anim |

---

## 6. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| PRD sections implemented | 14/14 | Per section checklist |
| Rendering time | < 200ms | Lighthouse/DevTools |
| Interactive response | < 100ms | User interaction timing |
| All tests pass | 100% | Jest/Testing Library |
| WebSocket reconnect | < 3s | Measured latency |
| Export quality | Good | Visual inspection |
| Dark mode consistency | Full | All components tested |

---

## 7. File Structure Output

```
NEW files to create:
├── apps/dashboard/src/
│   ├── app/visualization/
│   │   ├── page.tsx                        ← NEW: Full viz dashboard
│   │   ├── composite/page.tsx              ← NEW: Radar chart page
│   │   ├── macro/page.tsx                  ← NEW: Sentiment gauge page
│   │   ├── performance/page.tsx            ← NEW: Equity curve page
│   │   └── timeline/page.tsx               ← NEW: Trade timeline page
│   ├── app/replay/page.tsx                 ← NEW: History replay page
│   ├── components/charts/
│   │   ├── radar-chart.tsx                 ← NEW
│   │   ├── gauge-chart.tsx                 ← NEW
│   │   ├── waterfall-chart.tsx             ← NEW
│   │   ├── heatmap-chart.tsx               ← NEW
│   │   ├── equity-curve.tsx                ← NEW
│   │   ├── probability-bar.tsx             ← NEW
│   │   ├── alignment-matrix.tsx            ← NEW
│   │   ├── regime-timeline.tsx             ← NEW
│   │   └── decision-flow.tsx               ← NEW
│   ├── components/signal/
│   │   ├── confidence-ring.tsx             ← NEW
│   │   ├── quality-badge.tsx               ← NEW
│   │   ├── risk-meter.tsx                  ← NEW
│   │   ├── entry-ladder.tsx                ← NEW
│   │   └── rr-diagram.tsx                  ← NEW
│   ├── components/shared/
│   │   ├── loading-skeleton.tsx            ← NEW
│   │   └── websocket-status.tsx            ← NEW
│   └── lib/
│       ├── api-visualization.ts            ← NEW
│       └── websocket.ts                    ← NEW

MODIFIED files:
├── apps/dashboard/
│   ├── src/components/sidebar.tsx           ← Add new nav items
│   ├── src/app/signals/page.tsx             ← Integrate chart components
│   └── src/lib/api.ts                       ← Add new endpoints

BACKEND files (new):
├── apps/api/src/routers/visualization.py    ← NEW: V2 endpoints
├── apps/api/src/main.py                     ← Register new router
```

---

## 8. Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Recharts tidak support waterfall chart | Phase 6 delay | Custom SVG implementation (proven technique) |
| WebSocket complexity | Phase 2 delay | Start with polling fallback, add WS later |
| Backend data tidak tersedia | All phases | Mock data layer for development |
| Performance dengan 1000+ signals | Phase 3 | Virtualization, pagination from API |
| Dependency conflicts | Any phase | Pin versions, test in CI |

---

## 9. Rekomendasi

**Mulai dari Phase 1 (Sprint 1.1)** karena:
1. Tidak membutuhkan backend baru — data already available dari `/api/v1/unified-signal/{symbol}`
2. Semua component bisa di-render dengan mock data
3. Visible progress cepat — boosting morale
4. Foundation untuk phase selanjutnya

**Prioritas komponen pertama:**
1. `radar-chart.tsx` — Composite Score (paling berdampak, mudah)
2. `gauge-chart.tsx` — Macro Sentiment (high visibility)
3. `confidence-ring.tsx` — Signal Summary (iconic visual)
