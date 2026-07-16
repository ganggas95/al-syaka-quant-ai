# Development Plan: Live Signal Workspace

> **Branch:** `feature/live-signal-workspace`
> **PRD Reference:** `PRD_LIVE_SIGNAL_WORSKPACE.md`

---

## Analisis Kesenjangan (Gap Analysis)

| PRD Requirement | Current Status | Keterangan |
|---|---|---|
| Auto-generate signal on page load | ❌ Manual | Masih menggunakan tombol "Generate Signal" |
| Auto-refresh on Symbol/Timeframe change | ❌ Manual | Harus klik tombol setiap kali ganti |
| AI Market Thesis | ❌ Belum ada | Data dari API sudah tersedia |
| Consensus Multi-Timeframe | ⚠️ Parsial | Hanya label H1/H4/D1 tanpa visualisasi |
| Probability Visualization | ❌ Belum ada | Perlu visualisasi confidence yang lebih baik |
| Explainability (SHAP) | ❌ Belum ada di UI | SHAP data sudah ada di response API |
| Signal History Panel | ⚠️ Parsial | Hanya navigasi prev/next, belum ada full list |
| Signal Timeline | ❌ Belum ada | Timeline visual dari signal-signal sebelumnya |
| Risk Summary | ❌ Belum ada | Ringkasan risk, SL, TP, RR, position sizing |
| Session Information | ⚠️ Parsial | Sebagian ada di MarketStatusBar |
| Skeleton Loading | ✅ Existing | SignalSkeleton sudah ada |
| Progressive Loading | ❌ Belum ada | Loading bertahap per komponen |
| Error State | ⚠️ Minimal | Hanya menampilkan error message |
| Empty State | ❌ Belum ada | Tidak ada tampilan saat pertama kali load |
| Auto Refresh State | ❌ Belum ada | Indikator refresh subtle belum ada |
| Debounce Symbol/Timeframe | ❌ Belum ada | Perubahan langsung trigger fetch |
| Request Cancellation | ❌ Belum ada | Race condition saat ganti symbol cepat |
| Prevent Duplicate API Calls | ❌ Belum ada | Bisa terjadi multiple request |
| Cached Previous Signal | ❌ Belum ada | UI flash saat refresh data |
| Smooth UI Transition | ❌ Belum ada | Transisi component mount/unmount |

---

## Phase 1: Foundation & Auto-Generation

### 1.1. Refactor API Layer

**File target:** `apps/dashboard/src/lib/api.ts`

**Perubahan:**
- Tambahkan interface `UnifiedSignalResponse` yang merepresentasikan response dari `/api/v1/unified-signal/{symbol}`
- Tambahkan interface `SignalHistoryEntry`
- Buat function `fetchUnifiedSignal()` yang menggunakan `AbortController`
- Buat function `fetchOHLC()` yang menggunakan `AbortController`
- Export tipe-tipe baru untuk digunakan di komponen

**UnifiedSignalResponse fields yang perlu di-cover:**
- Signal dasar: `signal_id`, `symbol`, `timestamp`, `signal`, `confidence`
- Harga: `entry_price`, `stop_loss`, `take_profit`, `risk_reward`
- Multi-TF: `h1_signal`, `h4_signal`, `d1_signal`
- AI: `ai_confidence`, `ai_accuracy`, `shap_reasons`, `shap_summary`, `feature_contributions`, `explanation_reason`
- Composite: `composite_score`, `confidence_breakdown`, `confidence_label`
- Market: `market_regime`, `regime_reason`, `market_trend`, `market_structure`
- Makro: `macro_bias`, `macro_strength`, `macro_confidence`, `macro_reason`, `macro_events`
- Final Decision: `final_decision`, `decision_reason`, `conflict_detected`, `hedge_intensity`, `decision_confidence`, `position_multiplier`
- Risk: `risk_level`, `lot_size`, `trade_quality`
- Lainnya: `reasons`, `indicators_used`

---

### 1.2. Custom Hook: useAutoSignal

**File baru:** `apps/dashboard/src/hooks/use-auto-signal.ts`

**Fungsi:**
- `useEffect` untuk fetch signal saat mount (pertama kali halaman dibuka)
- `useEffect` untuk监听 perubahan `symbol` / `timeframe`
- **Debounce 300ms** untuk perubahan symbol dan timeframe
- **AbortController** untuk cancel request sebelumnya (mencegah race condition)
- **Previous signal cache** menggunakan `useRef` agar UI tidak flash saat refresh
- Prevent duplicate API calls menggunakan `useRef` untuk tracking loading state
- Mengembalikan: `{ result, candleData, signalHistory, loading, error, isRefreshing }`
- `isRefreshing` membedakan antara loading pertama (full skeleton) vs refresh (subtle indicator)

**State management:**
- `result`: data signal terbaru (atau cached data)
- `candleData`: data OHLC untuk chart
- `signalHistory`: array history signal (max 20 entries)
- `loading`: true hanya untuk loading pertama
- `isRefreshing`: true saat auto-refresh (loading sudah pernah sukses)
- `error`: error message jika fetch gagal

---

### 1.3. Loading & UX States

**File baru:** `apps/dashboard/src/components/signal/loading-states.tsx`

**Komponen:**
- `InitialLoadingState` - Full skeleton untuk loading pertama
- `RefreshIndicator` - Subtle loading bar/indicator untuk auto-refresh
- `ErrorState` - Error card dengan retry button
- `EmptyState` - Tampilan saat pertama kali (belum pernah load)

**File modifikasi:** `apps/dashboard/src/components/shared/loading-skeleton.tsx`
- Update `SignalSkeleton` agar lebih mirip layout dashboard baru

---

## Phase 2: Dashboard Components Baru

### 2.1. AI Market Thesis

**File baru:** `apps/dashboard/src/components/signal/ai-market-thesis.tsx`

**Deskripsi:**
Menampilkan thesis AI tentang kondisi market saat ini dalam bentuk card informatif.

**Data source:**
- `result.reasons` (array of reasons)
- `result.explanation_reason` (teks eksplanasi)
- `result.market_regime` + `result.regime_reason`
- `result.macro_bias` + `result.macro_reason`

**Layout:**
- Header: "AI Market Thesis" dengan ikon `BrainCircuit`
- Body: Teks eksplanasi yang diformat dengan baik
- Footer: Tags untuk regime, macro bias, dll

---

### 2.2. Consensus Multi-Timeframe

**File baru:** `apps/dashboard/src/components/signal/consensus-multitf.tsx`

**Deskripsi:**
Visualisasi konsensus sinyal dari multiple timeframe (H1, H4, D1).

**Data source:**
- `result.h1_signal` (arah sinyal H1)
- `result.h4_signal` (arah sinyal H4)
- `result.d1_signal` (arah sinyal D1)

**Layout:**
- Tiga kolom untuk H1, H4, D1
- Masing-masing menampilkan arah (BUY/SELL/NEUTRAL) dengan warna
- Progress bar untuk confidence masing-masing TF
- Arrow icon untuk arah

---

### 2.3. Probability Visualization

**File baru:** `apps/dashboard/src/components/signal/probability-visualization.tsx`

**Deskripsi:**
Visualisasi probability/confidence yang lebih informatif dari yang sudah ada.

**Data source:**
- `result.confidence`
- `result.confidence_label`
- `result.decision_confidence`

**Layout:**
- Large gauge/donut chart yang menunjukkan confidence level
- Warna dinamis: hijau (>=70%), biru (40-70%), merah (<40%)
- Label kualitatif: LOW / MEDIUM / HIGH / STRONG
- Animasi halus saat nilai berubah

---

### 2.4. Explainability (SHAP)

**File baru:** `apps/dashboard/src/components/signal/shap-explainability.tsx`

**Deskripsi:**
Menampilkan SHAP values untuk menjelaskan prediksi AI.

**Data source:**
- `result.shap_reasons`
- `result.shap_summary`
- `result.feature_contributions`

**Layout:**
- Horizontal bar chart (feature importance) menggunakan `recharts`
- Warna: merah (negative contribution), hijau (positive contribution)
- Tooltip yang menunjukkan nilai kontribusi
- Summary text di bagian bawah

---

### 2.5. Signal History

**File baru:** `apps/dashboard/src/components/signal/signal-history.tsx`

**Deskripsi:**
Panel yang menampilkan history signal dalam bentuk table/list.

**Data source:**
- `signalHistory` dari `useAutoSignal`

**Layout:**
- Table dengan kolom: Timestamp, Symbol, Signal, Confidence, TF
- Row yang sedang aktif di-highlight
- Scrollable (max 20 items)
- Filter by symbol (opsional)

---

### 2.6. Signal Timeline

**File baru:** `apps/dashboard/src/components/signal/signal-timeline.tsx`

**Deskripsi:**
Timeline visual yang menunjukkan kapan signal-signal dihasilkan.

**Data source:**
- `signalHistory` dari `useAutoSignal`

**Layout:**
- Vertical timeline dengan dot untuk setiap signal
- Warna dot sesuai arah signal (hijau BUY, merah SELL, abu-abu NEUTRAL)
- Label timestamp dan confidence
- Berguna untuk melihat pola/frekuensi signal

---

### 2.7. Risk Summary

**File baru:** `apps/dashboard/src/components/signal/risk-summary.tsx`

**Deskripsi:**
Ringkasan risk management untuk signal saat ini.

**Data source:**
- `result.risk_level`
- `result.stop_loss`, `result.take_profit`, `result.risk_reward`
- `result.lot_size`, `result.position_multiplier`
- `result.trade_quality`

**Layout:**
- Card grid dengan parameter SL, TP, RR
- Position sizing info (lot_size, multiplier)
- Risk level badge (LOW/MEDIUM/HIGH)
- Trade quality indicator

---

### 2.8. Session Information

**File baru:** `apps/dashboard/src/components/signal/session-info.tsx`

**Deskripsi:**
Informasi session trading saat ini.

**Data source:**
- `result.macro_events`
- `result.session` (jika ada di response)
- Atau kalkulasi dari waktu server

**Layout:**
- Menampilkan session aktif: London, New York, Asia, dll
- Status session (open/close)
- Dampak session terhadap volatilitas

---

## Phase 3: Dashboard Layout Redesign

### 3.1. Layout Restructuring

**File target:** `apps/dashboard/src/app/signals/page.tsx`

**New Layout Hierarchy:**

```
┌──────────────────────────────────────────────┐
│ HEADER CONTROLS (Symbol, Timeframe, dll)      │
├──────────────────────────────────────────────┤
│ SIGNAL STATUS BANNER (Signal, Confidence)      │
├──────────────────────────────────────────────┤
│ PARAMETERS ROW (Entry, SL, TP, RR)            │
├──────────────────────────────────────────────┤
│ AI MARKET THESIS                              │
├──────────────────────────────────────────────┤
│ CONSENSUS MTF │ PROBABILITY │ COMPOSITE SCORE │
├──────────────────────────────────────────────┤
│ PRICE CHART (full-width, larger)              │
├──────────────────────────────────────────────┤
│ MKT STRUCTURE │ SHAP EXPLAIN │ RISK SUMMARY   │
├──────────────────────────────────────────────┤
│ SIGNAL HISTORY │ SIGNAL TIMELINE              │
├──────────────────────────────────────────────┤
│ MARKET STATUS BAR + SESSION INFO              │
└──────────────────────────────────────────────┘
```

### 3.2. Responsive Layout

- Desktop (>=1024px): 3-column grid untuk komponen samping
- Tablet (768-1023px): 2-column grid
- Mobile (<768px): 1-column, stacked
- Collapsible sections untuk mobile (accordion pattern)

### 3.3. Smooth UI Transitions

- Tambahkan `animate-in` dan `fade-in` classes untuk component mount
- Transisi warna smooth untuk nilai yang berubah (confidence, price)
- `transition-all duration-300` untuk hover dan state changes

---

## Phase 4: Performance & Polish

### 4.1. Debounce Implementation

- **300ms debounce** untuk perubahan symbol
- **300ms debounce** untuk perubahan timeframe
- Implementasi menggunakan `setTimeout` + `clearTimeout` di custom hook

### 4.2. Request Cancellation

- Setiap fetch me-receive `AbortController.signal`
- Saat dependency berubah, cancel request sebelumnya:
  ```typescript
  controllerRef.current?.abort();
  controllerRef.current = new AbortController();
  ```
- Handle `AbortError` secara graceful (jangan trigger error state)

### 4.3. Prevent Duplicate API Calls

- Gunakan `useRef` untuk tracking request ID
- Setiap request mendapat incrementing ID
- Jika response datang dengan ID yang tidak cocok, discard

### 4.4. Cached Previous Signal

- Simpan result dan candleData terakhir di `useRef`
- Selama loading data baru, tampilkan cached data
- Saat data baru datang, smooth swap dari cached ke data baru
- Mencegah UI flash/blank saat refresh

---

## Ringkasan File yang Akan Dibuat/Dimodifikasi

### File Baru

```
apps/dashboard/src/
├── hooks/
│   └── use-auto-signal.ts                    # Custom hook auto-signal
├── components/
│   ├── signal/
│   │   ├── ai-market-thesis.tsx              # AI Market Thesis component
│   │   ├── consensus-multitf.tsx             # Multi-TF consensus component
│   │   ├── probability-visualization.tsx     # Probability visualization
│   │   ├── shap-explainability.tsx           # SHAP explainability component
│   │   ├── signal-history.tsx                # Signal history table
│   │   ├── signal-timeline.tsx               # Signal timeline component
│   │   ├── risk-summary.tsx                  # Risk summary component
│   │   ├── session-info.tsx                  # Session information component
│   │   └── loading-states.tsx                # Loading/error/empty states
```

### File yang Dimodifikasi

```
apps/dashboard/src/
├── lib/
│   └── api.ts                                # Tambah types + AbortController
├── components/
│   ├── shared/
│   │   └── loading-skeleton.tsx              # Update skeleton layout
│   ├── charts/
│   │   ├── score-breakdown.tsx               # Minor update (props/data)
│   │   └── market-status-bar.tsx             # Minor update (session info)
├── app/
│   └── signals/
│       └── page.tsx                          # Major redesign
```

---

## Dependencies

Tidak ada dependency baru. Semua komponen menggunakan libraries yang sudah ada di project:

| Library | Penggunaan |
|---|---|
| `recharts` | Bar chart, radar chart, pie/donut chart |
| `lucide-react` | Icons untuk semua komponen |
| `lightweight-charts` | Candlestick chart |
| `tailwindcss` | Styling, layout, animation |

---

## Success Criteria Checklist

- [ ] Halaman Signal auto-generate signal saat pertama kali dibuka
- [ ] Signal otomatis diperbarui saat Symbol berubah (dengan debounce 300ms)
- [ ] Signal otomatis diperbarui saat Timeframe berubah (dengan debounce 300ms)
- [ ] Tidak ada duplicate API calls saat user cepat berganti symbol/timeframe
- [ ] Request cancellation bekerja: request sebelumnya di-cancel saat yang baru dimulai
- [ ] Previous signal cache mencegah UI flash/blank saat refresh
- [ ] Loading pertama menampilkan skeleton yang sesuai layout
- [ ] Auto-refresh menampilkan indikator subtle (bukan full skeleton)
- [ ] Error state menampilkan card error dengan retry button
- [ ] Empty state menampilkan pesan informatif
- [ ] AI Market Thesis menampilkan analisis AI dengan jelas
- [ ] Consensus Multi-Timeframe menampilkan H1/H4/D1 signals
- [ ] Probability Visualization menampilkan confidence dengan visual yang menarik
- [ ] SHAP Explainability menampilkan feature contributions
- [ ] Signal History menampilkan 20 signal terakhir dalam table
- [ ] Signal Timeline menampilkan history dalam bentuk timeline visual
- [ ] Risk Summary menampilkan SL, TP, RR, position sizing
- [ ] Session Information menampilkan session trading aktif
- [ ] Layout responsif pada desktop (3-column) dan tablet (2-column)
- [ ] Transisi UI terasa halus (animasi, fade-in, color transition)
- [ ] Tidak ada perubahan pada core AI Trading Engine

---

## Catatan Tambahan

- **Prioritas:** Phase 1 > Phase 2 > Phase 3 > Phase 4
- **Dependency:** Phase 1 harus selesai sebelum Phase 3
- **Parallel work:** Phase 2 komponen bisa dikerjakan paralel setelah Phase 1 selesai
- **Testing:** Setiap komponen harus diuji dengan berbagai state (loading, error, empty, data)
- **Data flow:** Semua data mengalir dari `useAutoSignal` hook ke komponen-komponen child
