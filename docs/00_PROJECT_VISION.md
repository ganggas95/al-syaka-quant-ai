# Al-Syaka Quant AI -- Visi Proyek

## Visi

Menjadi platform analisis trading kuantitatif multi-asset terdepan yang menggabungkan kekuatan kecerdasan buatan, analisis market structure, dan manajemen risiko yang ketat untuk memberikan sinyal trading yang akurat, transparan, dan dapat dipertanggungjawabkan.

## Misi

1. **Mendemokratisasi Analisis Kuantitatif** -- Menyediakan alat analisis tingkat institusi yang dapat diakses oleh trader ritel dan profesional.
2. **Transparansi Black-Box AI** -- Setiap prediksi AI disertai penjelasan SHAP yang mudah dipahami, sehingga trader tahu mengapa suatu sinyal dihasilkan.
3. **Multi-Asset Coverage** -- Mendukung forex, komoditas (emas, perak), indeks saham, dan cryptocurrency dalam satu platform terpadu.
4. **Otomatisasi Cerdas** -- Menyediakan pipeline lengkap dari pengumpulan data, ekstraksi fitur, deteksi market structure, prediksi AI, hingga eksekusi trading otomatis melalui MT5.
5. **Manajemen Risiko Disiplin** -- Setiap sinyal trading dilengkapi dengan perhitungan posisi sizing, stop-loss, take-profit, dan Kelly criterion.

## Nilai Utama

| Nilai | Deskripsi |
|-------|-----------|
| **Akurasi** | Setiap komponen ditingkatkan secara berkelanjutan melalui backtesting dan validasi statistik. |
| **Transparansi** | Tidak ada keputusan kotak-hitam. Semua sinyal disertai breakdown confidence dan alasan. |
| **Disiplin Risiko** | Risk management bukan fitur tambahan, melainkan fondasi dari setiap sinyal yang dihasilkan. |
| **Modularitas** | Arsitektur monorepo memungkinkan setiap engine dikembangkan, diuji, dan ditingkatkan secara independen. |
| **Kinerja** | Optimasi untuk kecepatan eksekusi, dari pengumpulan data hingga pengambilan keputusan. |

## Target Pengguna

1. **Trader Retail** -- Mendapatkan sinyal trading harian dengan analisis teknikal, market structure, dan AI yang transparan.
2. **Trader Profesional** -- Menggunakan API untuk mengintegrasikan sinyal ke dalam sistem trading mereka sendiri.
3. **Analis Kuantitatif** -- Menggunakan backtest engine dan AI pipeline untuk mengembangkan dan menguji strategi baru.
4. **Manajer Portofolio** -- Memantau kinerja multi-symbol dan alokasi risiko secara real-time melalui dashboard.

## Platform Pillars

Al-Syaka Quant AI dibangun di atas lima pilar utama:

1. **Data Pipeline** -- Kolektor data multi-sumber dengan failover otomatis (Yahoo Finance, Polygon.io, Massive).
2. **Feature Engineering** -- Ekstraksi fitur dari data OHLC: candlestick patterns, momentum, volatilitas, session features.
3. **Market Structure Engine** -- Deteksi BOS (Break of Structure), CHOCH (Change of Character), FVG (Fair Value Gap), liquidity sweep, support & resistance.
4. **AI Engine** -- Model XGBoost, LightGBM, dan Transformer dengan explainability SHAP.
5. **Risk & Execution** -- Manajemen risiko terintegrasi, position sizing, Kelly criterion, dan koneksi MT5.

## Arsitektur Teknologi

- **Backend API**: Python FastAPI dengan SQLAlchemy async dan PostgreSQL.
- **AI/ML**: XGBoost, LightGBM, SHAP, scikit-learn.
- **Task Queue**: Celery dengan Redis sebagai broker.
- **Dashboard**: Next.js dengan lightweight-charts untuk visualisasi real-time.
- **Trading Bridge**: MT5 integration untuk eksekusi order.
- **Monorepo**: uv/pnpm workspace untuk manajemen package Python dan Node.js.
