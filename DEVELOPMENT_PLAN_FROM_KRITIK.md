# Perencanaan Pengembangan Berdasarkan Kritik

## 1. Ringkasan Analisa Kritik

Kritik ini secara keseluruhan positif. Fokus utamanya bukan pada kesalahan sistem, tetapi pada peluang untuk membuat sistem ini lebih profesional, lebih konsisten, dan lebih mudah dipercaya oleh trader.

### Yang sudah kuat

- Sistem sudah menggabungkan banyak layer analisis:
  - Market structure
  - Multi timeframe (H1/H4/D1)
  - EMA, ADX, RSI, ATR, MACD
  - Mean reversion
  - SHAP explanation
- Ini sudah lebih dekat ke Decision Support System daripada sekadar generator sinyal sederhana.

### Yang perlu diperbaiki

1. Confidence saat ini tidak cukup tepat jika diposisikan sebagai probabilitas murni.
2. Strategi seperti Mean Reversion perlu disesuaikan dengan market regime yang sedang berlangsung.
3. SHAP perlu dihadirkan lebih kuat sebagai penjelasan yang bisa dipahami trader.
4. Sistem masih belum memiliki konteks makro yang cukup kuat.
5. Perlu ada layer keputusan akhir yang lebih realistis, misalnya WAIT/HEDGE/BUY/SELL.

---

## 2. Tujuan Pengembangan

Membangun sistem trading intelligence yang:

- tidak hanya memproduksi sinyal,
- tetapi juga menjelaskan mengapa sinyal itu muncul,
- menilai kualitas sinyal secara transparan,
- dan mempertimbangkan konteks makro sebelum mengambil keputusan.

---

## 3. Prioritas Pengembangan

### Prioritas 1 — Rebuild Confidence menjadi Composite Score

**Masalah**

- Angka confidence 61% saat ini terasa seperti probabilitas, padahal belum tentu.

**Solusi**

- Ganti confidence menjadi composite score berbasis beberapa komponen:
  - Market structure: 35%
  - Momentum: 20%
  - Trend: 15%
  - Volatility: 10%
  - AI prediction: 20%
- Hasil akhir berupa score 0-100 yang lebih mudah dijelaskan.

**Output**

- `composite_score`
- `confidence_breakdown`
- `confidence_label` (Low / Medium / High)

---

### Prioritas 2 — Tambah Regime Detection

**Masalah**

- Mean reversion mungkin tidak relevan saat market sedang trending kuat.

**Solusi**

- Tambahkan engine yang mengklasifikasikan kondisi pasar menjadi:
  - Trending
  - Range
  - Reversal
  - Volatile
- Strategi yang dipakai disesuaikan dengan regime saat ini.

**Contoh logika**

- Jika market trending kuat → gunakan trend-following logic.
- Jika market ranging → gunakan mean reversion.
- Jika ada reversal pattern → gunakan breakout/reversal logic.

**Output**

- `market_regime`
- `strategy_mode`
- `regime_reason`

---

### Prioritas 3 — Perkuat Explainability dengan SHAP

**Masalah**

- SHAP saat ini belum cukup dioptimalkan untuk kebutuhan trader.

**Solusi**

- Tampilkan SHAP dalam bentuk yang trader pahami:
  - Top positive features
  - Top negative features
  - Feature contribution summary
  - Alasan natural language

**Output**

- `shap_summary`
- `feature_contributions`
- `explanation_reason`

---

### Prioritas 4 — Tambah Macro Sentiment Engine

**Masalah**

- Sistem teknikal sendiri tidak cukup untuk keputusan profesional.

**Solusi**

- Tambahkan layer makro yang membaca data seperti:
  - CPI
  - PPI
  - NFP
  - FOMC
  - DXY
  - 10Y Yield
  - Oil
  - Geopolitics / event risk
- Hasilnya menjadi `macro_bias`.

**Output**

- `macro_bias` (Bullish / Bearish / Neutral)
- `macro_strength`
- `macro_confidence`

---

### Prioritas 5 — Tambah Layer Keputusan Akhir

**Masalah**

- Saat ini sistem cenderung hanya menghasilkan BUY/SELL/NEUTRAL.

**Solusi**

- Tambahkan keputusan akhir yang lebih realistis:
  - BUY
  - SELL
  - WAIT
  - HEDGE

**Logika**

- Jika sinyal teknikal kuat, tetapi makro bertolak belakang → hasil akhir bisa WAIT atau HEDGE.

**Output**

- `final_decision`
- `decision_reason`
- `conflict_detected`

---

## 4. Roadmap Sprint

### Sprint 1 — Foundation & Composite Scoring (Minggu 1-2)

Tujuan: memperbaiki dasar interpretasi sinyal.

Tugas:

- Rebuild confidence scoring menjadi composite score.
- Tambahkan breakdown komponen confidence.
- Perbarui API response agar mengembalikan `composite_score`, `confidence_breakdown`, dan `confidence_label`.
- Perbarui frontend untuk menampilkan breakdown confidence secara visual.

Deliverable:

- Sinyal yang memiliki skor yang lebih transparan dan lebih realistis.

Exit Criteria:

- User dapat melihat score dan penjelasan komponennya di dashboard.
- Tidak ada regresi pada response API yang sudah ada.

---

### Sprint 2 — Market Regime Detection (Minggu 3-4)

Tujuan: membuat strategi lebih adaptif terhadap kondisi pasar.

Tugas:

- Tambahkan regime detector untuk mengklasifikasikan pasar menjadi Trending, Range, Reversal, atau Volatile.
- Hubungkan regime dengan pemilihan strategi.
- Pastikan strategi mean reversion hanya dipakai saat regime cocok.
- Tambahkan `market_regime`, `strategy_mode`, dan `regime_reason` ke output.

Deliverable:

- Strategi adaptif berdasarkan kondisi pasar.

Exit Criteria:

- Setiap sinyal mengandung klasifikasi regime yang masuk akal.
- Strategi berubah secara otomatis sesuai regime.

---

### Sprint 3 — Explainability & Trader UX (Minggu 5-6)

Tujuan: membuat sistem lebih dipercaya oleh pengguna.

Tugas:

- Perluas SHAP explanation menjadi ringkasan yang lebih trader-friendly.
- Tampilkan top positive features, top negative features, dan summary kontribusi fitur.
- Tambahkan penjelasan natural language untuk alasan sinyal.
- Perbaiki tampilan dashboard agar penjelasan lebih mudah dibaca.

Deliverable:

- UI yang menjawab pertanyaan: “Mengapa sistem memilih sinyal ini?”.

Exit Criteria:

- Pengguna bisa memahami alasan utama sinyal hanya dari satu layar.
- Penjelasan SHAP tidak lagi terasa teknis dan terlalu raw.

---

### Sprint 4 — Macro Sentiment Layer (Minggu 7-8)

Tujuan: menambah konteks makro ke dalam keputusan.

Tugas:

- Integrasi data ekonomi dan event calendar sederhana.
- Bangun macro bias engine dengan output `macro_bias`, `macro_strength`, dan `macro_confidence`.
- Hubungkan macro bias dengan pipeline sinyal teknikal.

Deliverable:

- Sistem sinyal yang mempertimbangkan teknikal + makro.

Exit Criteria:

- Macro bias muncul di output sinyal dan bisa dipakai sebagai bagian dari evaluasi.
- Ada perbedaan jelas antara sinyal bullish teknikal dan sinyal yang dikendalikan oleh konteks makro.

---

### Sprint 5 — Final Decision Layer (Minggu 9-10)

Tujuan: menambahkan layer keputusan akhir yang lebih realistis.

Tugas:

- Tambahkan keputusan akhir dengan opsi BUY, SELL, WAIT, atau HEDGE.
- Bangun logika conflict handling antara sinyal teknikal dan macro bias.
- Tambahkan `final_decision`, `decision_reason`, dan `conflict_detected` ke output.

Deliverable:

- Sistem yang tidak hanya memberi sinyal, tetapi juga merekomendasikan langkah yang lebih bijak.

Exit Criteria:

- Saat teknikal kuat namun makro bertentangan, sistem bisa menghasilkan WAIT atau HEDGE.
- Keputusan akhir memiliki alasan yang dapat dijelaskan.

---

### Sprint 6 — Validation, Backtesting & Hardening (Minggu 11-12)

Tujuan: memastikan sistem konsisten dan dapat dipercaya.

Tugas:

- Tambahkan backtest untuk composite score, regime engine, dan final decision logic.
- Bandingkan performa tiap mode strategi dan regime.
- Simpan metrik performa per simbol, timeframe, dan periode waktu.
- Perbaiki edge case, error handling, dan pengalaman pengguna.

Deliverable:

- Evidence-based validation untuk sistem.

Exit Criteria:

- Ada data backtest yang dapat dipakai untuk evaluasi performa.
- Sistem siap untuk tahap pilot atau pengujian pengguna.

---

## 5. Indikator Keberhasilan

Sistem dianggap berkembang jika:

- confidence lebih mudah dipahami oleh trader,
- setiap sinyal punya penjelasan yang jelas,
- regime detection benar-benar memengaruhi strategi,
- macro bias mulai terlihat di output,
- final decision bisa menolak sinyal yang terlalu konflik,
- dashboard mampu menunjukkan semua ini secara intuitif.

---

## 6. Rekomendasi Implementasi Selanjutnya

Langkah pertama yang paling penting adalah:

1. ganti confidence menjadi composite score,
2. tambahkan market regime detection,
3. lalu sambungkan dengan macro bias engine.

Dengan urutan ini, project akan berkembang dari sekadar signal generator menjadi true decision support system.
