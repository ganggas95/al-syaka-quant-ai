# Task Implementasi Sprint

Dokumen ini berisi task yang dapat dipakai sebagai backlog implementasi berdasarkan roadmap. Setiap task dilengkapi dengan kriteria selesai dan indikator apakah task tersebut sudah benar-benar selesai.

---

## Sprint 1 — Foundation & Composite Scoring

### Task 1.1 — Implementasi Composite Score

**Tujuan:** Mengganti confidence sederhana menjadi composite score yang lebih transparan.

**Pekerjaan:**

- Menentukan formula pembobotan untuk composite score.
- Menghitung score berdasarkan komponen teknikal dan AI.
- Menyimpan hasil ke response API.

**Kriteria selesai:**

- [ ] API mengembalikan field `composite_score`.
- [ ] API mengembalikan field `confidence_breakdown`.
- [ ] API mengembalikan field `confidence_label`.
- [ ] Nilai score berada dalam rentang 0–100.
- [ ] Score dapat dijelaskan secara logis dari komponen pembentuknya.

**Kriteria belum selesai / blocker:**

- [ ] Jika salah satu field tidak muncul atau nilainya tidak konsisten, task belum selesai.

---

### Task 1.2 — Tampilkan Breakdown Confidence di Dashboard

**Tujuan:** Membuat pengguna bisa melihat mengapa score muncul.

**Pekerjaan:**

- Menambahkan panel breakdown score di halaman sinyal.
- Menampilkan bobot dan kontribusi tiap komponen.
- Menata tampilan agar mudah dibaca.

**Kriteria selesai:**

- [ ] Dashboard menampilkan composite score secara jelas.
- [ ] Dashboard menampilkan breakdown tiap komponen.
- [ ] UI tidak rusak pada mode desktop maupun mobile.

**Kriteria belum selesai / blocker:**

- [ ] Jika breakdown tidak tampil atau terlihat ambigu, task belum selesai.

---

## Sprint 2 — Market Regime Detection

### Task 2.1 — Bangun Regime Detector

**Tujuan:** Mengklasifikasikan kondisi pasar menjadi regime yang jelas.

**Pekerjaan:**

- Menambahkan logic klasifikasi pasar.
- Mendeteksi kondisi Trending, Range, Reversal, dan Volatile.
- Menentukan alasan klasifikasi berdasarkan data teknikal.

**Kriteria selesai:**

- [ ] Sistem mampu mengidentifikasi minimal 4 regime.
- [ ] Output mengandung `market_regime`.
- [ ] Output mengandung `regime_reason`.

**Kriteria belum selesai / blocker:**

- [ ] Jika regime selalu sama atau tidak konsisten, task belum selesai.

---

### Task 2.2 — Hubungkan Regime ke Strategi

**Tujuan:** Membuat strategi adaptif terhadap regime.

**Pekerjaan:**

- Menghubungkan regime ke pemilihan strategi.
- Mengatur strategi yang cocok untuk tiap regime.
- Menyesuaikan logika mean reversion agar tidak dipakai saat tidak relevan.

**Kriteria selesai:**

- [ ] Strategi berubah otomatis berdasarkan regime.
- [ ] Mean reversion hanya dipakai saat regime yang sesuai.
- [ ] Output mengandung `strategy_mode`.

**Kriteria belum selesai / blocker:**

- [ ] Jika strategi tetap sama di semua regime, task belum selesai.

---

## Sprint 3 — Explainability & Trader UX

### Task 3.1 — Perkuat SHAP Explanation

**Tujuan:** Membuat penjelasan model lebih mudah dipahami trader.

**Pekerjaan:**

- Menyusun ringkasan SHAP yang lebih ringkas.
- Menampilkan fitur positif dan negatif secara terpisah.
- Menambahkan penjelasan naratif sederhana.

**Kriteria selesai:**

- [ ] Tersedia `shap_summary`.
- [ ] Tersedia `feature_contributions`.
- [ ] Tersedia `explanation_reason`.
- [ ] Penjelasan bisa dipahami tanpa membaca code.

**Kriteria belum selesai / blocker:**

- [ ] Jika output masih terlalu teknis dan tidak dimengerti, task belum selesai.

---

### Task 3.2 — Perbaiki UI Penjelasan Sinyal

**Tujuan:** Membuat penjelasan sinyal lebih intuitif di UI.

**Pekerjaan:**

- Menampilkan penjelasan SHAP di halaman sinyal.
- Menata layout sehingga ringkas dan mudah dibaca.
- Menambahkan visualisasi sederhana jika perlu.

**Kriteria selesai:**

- [ ] Pengguna dapat melihat alasan sinyal dalam satu layar.
- [ ] Tampilan tidak berantakan dan mudah dipahami.
- [ ] Tidak ada elemen yang hilang atau tidak ter-render.

**Kriteria belum selesai / blocker:**

- [ ] Jika pengguna masih bingung membaca alasan sinyal, task belum selesai.

---

## Sprint 4 — Macro Sentiment Layer

### Task 4.1 — Bangun Macro Bias Engine

**Tujuan:** Menambahkan konteks makro ke sistem.

**Pekerjaan:**

- Mengintegrasikan data ekonomi dan event calendar sederhana.
- Menentukan bias makro bullish, bearish, atau neutral.
- Menambahkan tingkat kekuatan dan confidence makro.

**Kriteria selesai:**

- [ ] Sistem menghasilkan `macro_bias`.
- [ ] Sistem menghasilkan `macro_strength`.
- [ ] Sistem menghasilkan `macro_confidence`.

**Kriteria belum selesai / blocker:**

- [ ] Jika output makro tidak muncul atau tidak masuk akal, task belum selesai.

---

### Task 4.2 — Hubungkan Macro Bias ke Sinyal

**Tujuan:** Menggabungkan sinyal teknikal dan konteks makro.

**Pekerjaan:**

- Menghubungkan hasil macro bias ke pipeline sinyal utama.
- Menentukan bagaimana macro mempengaruhi keputusan.

**Kriteria selesai:**

- [ ] Macro bias terhubung ke output sinyal utama.
- [ ] Ada indikasi perubahan sinyal akibat konteks makro.

**Kriteria belum selesai / blocker:**

- [ ] Jika macro bias tidak mempengaruhi output apa pun, task belum selesai.

---

## Sprint 5 — Final Decision Layer

### Task 5.1 — Implementasi Final Decision

**Tujuan:** Memberikan keputusan akhir yang lebih realistis.

**Pekerjaan:**

- Menambahkan opsi keputusan BUY, SELL, WAIT, dan HEDGE.
- Menentukan logika final decision berdasarkan sinyal teknikal dan macro.

**Kriteria selesai:**

- [ ] Output mengandung `final_decision`.
- [ ] Output mengandung `decision_reason`.
- [ ] Output mengandung `conflict_detected`.

**Kriteria belum selesai / blocker:**

- [ ] Jika keputusan akhir tidak ada atau tidak konsisten, task belum selesai.

---

### Task 5.2 — Implementasi Conflict Handling

**Tujuan:** Menangani situasi ketika teknikal dan makro saling bertolak belakang.

**Pekerjaan:**

- Membuat logika untuk menghindari keputusan yang terlalu agresif saat ada konflik.
- Menentukan apakah hasil akhir menjadi WAIT atau HEDGE.

**Kriteria selesai:**

- [ ] Sistem mampu mengenali konflik antara sinyal teknikal dan makro.
- [ ] Sistem menghasilkan keputusan yang lebih konservatif saat terdapat konflik.

**Kriteria belum selesai / blocker:**

- [ ] Jika sistem tetap memaksakan keputusan agresif saat ada konflik, task belum selesai.

---

## Sprint 6 — Validation, Backtesting & Hardening

### Task 6.1 — Tambah Backtesting untuk Feature Baru

**Tujuan:** Memastikan sistem tidak hanya bagus secara visual, tetapi juga konsisten.

**Pekerjaan:**

- Menambahkan backtest untuk composite score.
- Menambahkan backtest untuk regime engine.
- Menambahkan evaluasi untuk final decision logic.

**Kriteria selesai:**

- [ ] Tersedia hasil backtest untuk setidaknya satu skenario.
- [ ] Metrik performa dapat dibaca dan dibandingkan.

**Kriteria belum selesai / blocker:**

- [ ] Jika tidak ada hasil evaluasi yang bisa dipakai, task belum selesai.

---

### Task 6.2 — Stabilitas & Error Handling

**Tujuan:** Menjadikan sistem lebih siap digunakan.

**Pekerjaan:**

- Menangani kondisi error saat data tidak tersedia.
- Memastikan output aman saat data incomplete.
- Membersihkan edge case yang muncul selama pengujian.

**Kriteria selesai:**

- [ ] Sistem tidak crash saat data tidak lengkap.
- [ ] Error ditangani dengan pesan yang jelas.
- [ ] Semua task utama sudah lolos uji basic.

**Kriteria belum selesai / blocker:**

- [ ] Jika sistem masih sering gagal saat data tidak lengkap, task belum selesai.

---

## Panduan Penilaian Status Task

Gunakan aturan berikut saat menandai task:

- **Belum mulai**: task belum dikerjakan.
- **Dalam progres**: task sedang dikerjakan, tetapi belum selesai.
- **Selesai**: semua kriteria selesai terpenuhi.
- **Bloker**: task tidak bisa dilanjutkan karena ada masalah dependencies atau data.
