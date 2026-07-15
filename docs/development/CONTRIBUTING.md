# Panduan Kontribusi - Al-Syaka Quant AI

Terima kasih atas minat Anda untuk berkontribusi pada project Al-Syaka Quant AI. Dokumen ini berisi panduan untuk berkontribusi secara efektif dan konsisten.

---

## Branch Strategy

Kami menggunakan strategi branching berikut:

```
main
  |-- develop
       |-- feature/nama-fitur
       |-- fix/nama-bug
       |-- refactor/nama-refactor
       |-- docs/nama-dokumen
```

### Branch Rules

| Branch | Base | Deskripsi |
|--------|------|-----------|
| `main` | - | Production-ready code. Hanya diisi dari `develop` via merge request. |
| `develop` | `main` | Integration branch untuk pengembangan aktif. |
| `feature/*` | `develop` | Fitur baru. Prefix: `feature/`. |
| `fix/*` | `develop` | Perbaikan bug. Prefix: `fix/`. |
| `refactor/*` | `develop` | Refactoring kode. Prefix: `refactor/`. |
| `docs/*` | `develop` | Dokumentasi. Prefix: `docs/`. |

### Branch Naming Convention

Gunakan lowercase dengan tanda hubung:

```
feature/unified-signal-generator
fix/data-collector-timeout
refactor/move-indicators-to-package
docs/add-api-specification
```

---

## Workflow Kontribusi

### 1. Membuat Branch Baru

```bash
git checkout develop
git pull origin develop
git checkout -b feature/nama-fitur
```

### 2. Mengembangkan Fitur

- Ikuti standar coding yang tercantum di `CODING_STANDARD.md`
- Tulis unit test untuk fungsionalitas baru
- Pastikan semua test lulus sebelum commit
- Update dokumentasi jika diperlukan

### 3. Commit

Gunakan conventional commits:

```
feat(nama-modul): Deskripsi perubahan dalam 50 karakter

Penjelasan tambahan jika diperlukan. Bisa lebih dari satu
paragraf. Wrap di 72 karakter.

Closes #123
```

**Tipe Commit:**

| Tipe | Penggunaan |
|------|------------|
| `feat` | Fitur baru |
| `fix` | Perbaikan bug |
| `refactor` | Refactoring kode |
| `docs` | Dokumentasi |
| `test` | Penambahan atau perbaikan test |
| `chore` | Tugas maintenance (dependencies, config) |
| `style` | Perubahan formatting (bukan logic) |
| `perf` | Optimasi performa |

### 4. Push dan Merge Request

```bash
git push origin feature/nama-fitur
```

Kemudian buat Merge Request (MR) ke branch `develop`.

### 5. Code Review

Setiap MR membutuhkan minimal 1 approval sebelum di-merge.

---

## Pull Request / Merge Request Process

### Template MR

```markdown
## Deskripsi

Penjelasan singkat tentang apa yang diubah dan mengapa.

## Related Issues

Closes #123

## Type of Change

- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing

- [ ] Unit tests passing
- [ ] Manual testing done
- [ ] No regression

## Checklist

- [ ] Kode mengikuti standar coding project
- [ ] Type hints sudah ditambahkan
- [ ] Docstrings sudah ditambahkan
- [ ] Tidak ada debug code atau commented code
- [ ] Environment variables tidak di-commit
- [ ] Dokumentasi diupdate (jika perlu)
```

### MR Size Guidelines

- Usahakan MR tidak lebih dari 400 baris perubahan
- Jika lebih besar, pecah menjadi beberapa MR yang lebih kecil
- Setiap MR harus fokus pada satu perubahan logis

### Review Turnaround

- Reviewer harus merespon dalam 1x24 jam
- Untuk perubahan kecil, review bisa dilakukan dalam beberapa jam
- Jika perubahan urgent, tag reviewer di Slack/Discord

---

## Code Review Guidelines

### Untuk Reviewer

#### Apa yang Dicek

1. **Kebenaran:** Apakah kode melakukan apa yang seharusnya?
2. **Konsistensi:** Apakah mengikuti standar coding dan pola project?
3. **Kinerja:** Apakah ada bottleneck potensial?
4. **Keamanan:** Apakah ada celah keamanan? (SQL injection, XSS, dll)
5. **Error Handling:** Apakah error ditangani dengan tepat?
6. **Testing:** Apakah ada test untuk perubahan ini?
7. **Dokumentasi:** Apakah dokumentasi diupdate?

#### Cara Memberi Review

- Berikan komentar yang spesifik dan konstruktif
- Jelaskan "mengapa" suatu perubahan diperlukan
- Gunakan format: `[Saran]` untuk saran, `[Harus]` untuk yang wajib diperbaiki
- Apresiasi kode yang baik

Contoh review yang baik:

```
[Saran] Di sini kita bisa menggunakan `dataclass` daripada
class biasa untuk SignalResult, karena ini hanya objek data
dan tidak perlu method. Contohnya sudah ada di file
signal_service/generator.py.
```

### Untuk Pengembang (Reviewee)

- Jangan defensif, terima feedback sebagai kesempatan belajar
- Jika tidak setuju, jelaskan alasannya secara profesional
- Setelah revisi, beri tahu reviewer via komentar
- Gunakan "Resolve conversation" setelah issue terselesaikan

---

## Testing Guidelines

### Python

```bash
# Jalankan semua test
pytest

# Jalankan test dengan coverage
pytest --cov=src --cov-report=term-missing

# Jalankan test spesifik
pytest tests/test_signal_generator.py -v

# Type checking
mypy src/

# Linting
ruff check src/
```

### TypeScript

```bash
# Jalankan test
pnpm --filter dashboard test

# Type checking
pnpm --filter dashboard type-check

# Linting
pnpm --filter dashboard lint
```

### Test Coverage Target

| Layer | Target Coverage |
|-------|-----------------|
| API routers | 80% |
| Signal service | 85% |
| Market structure | 85% |
| AI models | 75% |
| Backtesting engine | 85% |
| Dashboard components | 70% |

---

## Dokumentasi

### Kapan Perlu Update Dokumentasi

- Menambahkan endpoint API baru
- Mengubah skema database
- Menambah atau mengubah alur bisnis
- Mengubah konfigurasi environment
- Menambah package dependencies baru

### Lokasi Dokumentasi

| Konten | Lokasi |
|--------|--------|
| API Specification | `docs/api/API_SPEC.md` |
| Database Schema | `docs/api/DATABASE_SCHEMA.md` |
| Event Flow | `docs/api/EVENT_FLOW.md` |
| WebSocket Spec | `docs/api/WEBSOCKET_SPEC.md` |
| Coding Standard | `docs/development/CODING_STANDARD.md` |
| Agent Rules | `docs/development/AGENT_RULES.md` |
| Task Tracking | `docs/development/TASKS.md` |
| Changelog | `docs/development/CHANGELOG.md` |

---

## Environment Setup

### Prasyarat

- Python 3.12+
- Node.js 18+
- pnpm 9+
- PostgreSQL 16+
- Redis 7+

### Langkah Instalasi

```bash
# Clone repository
git clone https://github.com/username/al-syaka-quant-ai.git
cd al-syaka-quant-ai

# Setup Python virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# atau
.venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -e packages/common
pip install -e packages/indicators
pip install -e packages/feature-engineering
pip install -e packages/quant
pip install -e packages/risk
pip install -e apps/api
pip install -e apps/ai-engine
pip install -e apps/backtester
pip install -e apps/mt5-bridge

# Install Node.js dependencies
pnpm install

# Setup database
cp .env.example .env
# Edit .env dengan konfigurasi database Anda
alembic upgrade head

# Seed data
python database/seed/symbols.py

# Jalankan development server
# Terminal 1: API
uvicorn src.main:app --reload

# Terminal 2: Dashboard
pnpm dev:dashboard

# Terminal 3: Celery worker
celery -A src.celery_app worker --loglevel=info

# Terminal 4: Celery beat
celery -A src.celery_app beat --loglevel=info
```

---

## Etika dan Panduan

1. **Berkomunikasi dengan Hormat:** Semua diskusi harus profesional dan saling menghormati.
2. **Berbagi Pengetahuan:** Jika menemukan solusi menarik, dokumentasikan di wiki atau bagikan di channel team.
3. **Mengedepankan Kualitas:** Kualitas kode lebih penting daripada kecepatan deliver.
4. **Dokumentasi:** Jika sesuatu sulit dijelaskan dalam kode, tambahkan komentar atau dokumentasi.
5. **Keamanan:** Jangan commit credentials, API keys, atau informasi sensitif lainnya.

---

## Sumber Daya

- **API Docs:** http://localhost:8000/docs
- **Dashboard:** http://localhost:3000
- **Dokumentasi Project:** `/docs/`
- **Task Tracking:** `/docs/development/TASKS.md`
