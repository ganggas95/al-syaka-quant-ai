# Backtesting Dashboard UI Optimization

## PRD - Frontend Performance & UX Improvement

Version: 1.0

---

# Objective

Melakukan optimasi Dashboard Backtesting agar tetap responsif ketika jumlah trade mencapai ratusan hingga ribuan tanpa mengubah logic backend, engine backtesting, maupun algoritma trading.

Fokus pengembangan hanya pada:

- Frontend Rendering
- Data Visualization
- User Experience
- Performance Rendering

Backend harus tetap menghasilkan output JSON yang sama seperti saat ini.

---

# Goals

Target dashboard:

- Smooth ketika trade > 1000
- Tidak terjadi UI Freeze
- Tidak ada lag saat Zoom
- Tidak ada lag saat Scroll
- Tidak ada lag saat Hover
- Tetap mempertahankan seluruh informasi penting

---

# Out of Scope

Branch ini TIDAK BOLEH mengubah:

- Engine Backtesting
- Signal Generator
- AI Model
- Strategy
- Risk Management
- Position Sizing
- Database
- API Contract
- Response JSON

Semua perubahan hanya berada pada sisi frontend.

---

# Current Problems

## 1. Terlalu banyak marker

Contoh:

978 trades menghasilkan:

- Entry Marker
- Exit Marker
- TP Marker
- SL Marker
- Profit Label

Total object yang dirender bisa mencapai ribuan.

Browser menjadi berat.

---

## 2. Semua marker dirender sekaligus

Walaupun user hanya melihat sebagian chart.

Semua trade tetap dibuat.

Inefisien.

---

## 3. Label Profit memenuhi chart

Contoh:

SELL +45

SELL -28

BUY +10

BUY +85

dst.

Text rendering jauh lebih mahal daripada line rendering.

---

## 4. Zoom tetap merender seluruh object

Semakin banyak trade,
semakin lambat.

---

## 5. Chart kehilangan keterbacaan

Trade saling menumpuk.

Sulit dianalisa.

---

# Solution Architecture

Menggunakan pendekatan:

Level of Detail (LOD)

Semakin jauh zoom,
semakin sedikit object yang dirender.

---

# Phase 1

## Viewport Culling

### Objective

Render hanya trade yang berada pada area chart yang sedang terlihat.

---

Current

Render:

978 trade

↓

User hanya melihat

20 trade

Tetapi browser tetap membuat 978 marker.

---

Target

```
Visible Area

|---------------------------|

Render:

Trade 120
Trade 121
Trade 122

Trade lainnya

SKIP
```

---

Acceptance Criteria

- hanya visible trade yang dirender
- marker otomatis berubah saat pan
- marker otomatis berubah saat zoom

---

# Phase 2

## Zoom Level Rendering

Semakin jauh zoom

↓

semakin sedikit informasi.

---

Zoom Out

Render

- Price

- Equity

- Drawdown

Tidak ada marker.

---

Medium Zoom

Render

Entry

Exit

Tanpa label.

---

Close Zoom

Render

Entry

Exit

TP

SL

Profit

Tooltip

---

Acceptance Criteria

Zoom tidak menyebabkan FPS drop.

---

# Phase 3

## Trade Clustering

Jika banyak trade pada area yang sama

Jangan render satu per satu.

---

Current

SELL

SELL

SELL

SELL

SELL

BUY

BUY

BUY

---

Target

```
+8 Trades
```

Klik

↓

Expand

```
SELL 5

BUY 3
```

---

Acceptance Criteria

Marker overlap berkurang drastis.

---

# Phase 4

## Tooltip Only

Profit tidak lagi ditampilkan permanen.

Current

SELL +45

SELL -12

BUY +80

SELL +10

---

Target

Marker

●

Hover

```
SELL

Profit

+$45

Duration

12 Candle

RR

2.1

Confidence

82%
```

---

Acceptance Criteria

Tidak ada lagi ribuan label text.

---

# Phase 5

## Marker Filtering

Tambahkan filter

☑ BUY

☑ SELL

☑ WIN

☑ LOSS

☑ TP

☑ SL

☑ ENTRY

☑ EXIT

☑ High Confidence

☑ Low Confidence

---

Acceptance Criteria

Marker mengikuti filter.

---

# Phase 6

## Trade Density View

Saat zoom jauh

Jangan tampilkan trade.

Gunakan density.

Misalnya

September

███████

Oktober

██████████████

November

██

Trader cukup melihat

bulan mana yang aktif.

---

Acceptance Criteria

Trade density terlihat jelas.

---

# Phase 7

## Heatmap Overlay

Alternatif visualisasi

Semakin terang

↓

Semakin banyak trade.

Tidak perlu marker.

---

Acceptance Criteria

Heatmap muncul hanya pada zoom jauh.

---

# Phase 8

## Lazy Marker Rendering

Render marker bertahap.

Misalnya

100

↓

Scroll

↓

100 berikutnya.

---

Acceptance Criteria

Tidak ada freeze saat membuka chart.

---

# Phase 9

## Chart Rendering Optimization

Gunakan:

Canvas Rendering

atau

Native Primitive

Hindari:

- HTML Marker
- DOM Node
- SVG banyak

---

Acceptance Criteria

Render >1000 marker tetap smooth.

---

# Phase 10

## Progressive Detail

Saat zoom

Overview

↓

Cluster

↓

Marker

↓

Detail

↓

Tooltip

Semakin dekat

Semakin detail.

---

# New Visualization Hierarchy

Level 0

Summary Card

↓

Level 1

Price

↓

Level 2

Equity

↓

Level 3

Drawdown

↓

Level 4

Trade Density

↓

Level 5

Cluster Marker

↓

Level 6

Entry Exit

↓

Level 7

SL TP

↓

Level 8

Tooltip

---

# UX Improvements

Tambahkan:

Mini Map

Navigator

Trade Search

Jump To Trade

Trade Timeline

Hide All Labels

Show Winning Only

Show Losing Only

Confidence Filter

Session Filter

Date Filter

---

# Performance KPI

Target

Chart Load

< 1 detik

Pan

60 FPS

Zoom

60 FPS

Hover

<100 ms

Filter

<200 ms

Marker Update

<300 ms

Trade

1000+

Tetap smooth

---

# Success Metrics

Dashboard dianggap berhasil apabila:

✅ 1000 trade dapat ditampilkan tanpa freeze

✅ Zoom tetap responsif

✅ Scroll tetap smooth

✅ Marker tidak saling bertumpuk

✅ Chart mudah dibaca

✅ Tidak ada perubahan backend

✅ Tidak ada perubahan API

✅ Tidak ada perubahan engine backtesting

---

# Deliverables

- Viewport Culling
- Zoom-based Rendering (LOD)
- Trade Clustering
- Tooltip-only Profit Display
- Marker Filtering
- Trade Density Visualization
- Heatmap Overlay
- Lazy Marker Rendering
- Canvas/WebGL Rendering Optimization
- Progressive Detail Rendering
- Mini Map Navigator
- Trade Search & Jump
- Responsive Performance
- Performance Benchmark Report

---

# Definition of Done

Semua poin berikut harus terpenuhi:

- Dashboard tetap menggunakan backend yang sama.
- Tidak ada perubahan logic backtesting.
- Tidak ada perubahan API.
- Chart tetap akurat.
- UI tetap responsif pada >1000 trade.
- Marker mudah dibaca.
- Tidak terjadi browser freeze.
- Dashboard siap digunakan untuk analisis profesional.
