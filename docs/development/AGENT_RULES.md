# Aturan untuk AI Agent - Al-Syaka Quant AI

## Prinsip Dasar

Dokumen ini berisi aturan yang harus diikuti oleh AI agent (seperti Claude Code, Copilot, atau Cursor) ketika diminta mengerjakan task dalam project Al-Syaka Quant AI.

---

## Aturan Umum

### 1. Baca Sebelum Menulis

Sebelum membuat perubahan pada file yang sudah ada, baca file tersebut terlebih dahulu secara lengkap. Pahami konteks dan struktur kode sebelum memodifikasi.

### 2. Konsistensi

Ikuti pola dan gaya kode yang sudah ada dalam project. Jangan mencampur gaya baru dengan gaya lama.

- Jika project menggunakan `@dataclass`, jangan ubah ke class biasa
- Jika project menggunakan `snake_case`, jangan gunakan `camelCase`
- Jika error handling menggunakan pola tertentu, ikuti pola tersebut

### 3. Minimal Changes

Buat perubahan seminimal mungkin untuk mencapai tujuan task. Jangan refaktor kode yang tidak terkait.

```
BENAR:  Memodifikasi satu function untuk menambah fitur
SALAH:  Merestruktur ulang seluruh module hanya untuk menambah satu endpoint
```

### 4. Jangan Tambahkan Dependency Baru

Sebelum menambah dependency baru, periksa `pyproject.toml` atau `package.json` project untuk melihat apakah library yang dibutuhkan sudah tersedia.

### 5. Jangan Buat File Tak Perlu

Hanya buat file baru jika benar-benar diperlukan. Jika fungsionalitas dapat ditambahkan ke file yang sudah ada, lakukan di sana.

---

## Aturan Python

### 1. Type Hints Wajib

Semua fungsi dan method harus memiliki type hints. Jangan biarkan parameter tanpa tipe.

### 2. Async Pattern

Gunakan pola async yang konsisten:

```python
# Untuk fungsi yang melakukan I/O
async def get_data(session: AsyncSession) -> list[Symbol]:
    result = await session.execute(select(Symbol))
    return result.scalars().all()
```

### 3. Error Boundary

Setiap function yang bisa gagal harus menangani error dengan tepat:

- Gunakan `try/except` hanya di boundary layer (API router, task entry point)
- Biarkan exception propagate ke layer yang lebih tinggi
- Log exception sebelum melempar ulang

### 4. Database Operations

```python
# SELALU gunakan async session
async with async_session_factory() as session:
    try:
        session.add(record)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

### 5. Import Celery

```python
# Task Celery harus menggunakan @shared_task
@shared_task(name="task_name", bind=True, max_retries=3)
def my_task(self):
    ...
```

---

## Aturan FastAPI

### 1. Router Prefix

Semua router harus memiliki prefix dan tags:

```python
router = APIRouter(prefix="/api/v1/resource", tags=["resource"])
```

### 2. Response Model

Gunakan response model atau dict return type. Jangan return ORM objects langsung.

### 3. Error Response

Gunakan `HTTPException` untuk error response:

```python
raise HTTPException(status_code=404, detail=f"Resource {id} not found")
```

### 4. Parameter Validation

Gunakan `Query`, `Path`, `Body` dari FastAPI untuk validasi parameter.

---

## Aturan TypeScript/React

### 1. Type Safety

Semua props dan state harus memiliki tipe. Jangan gunakan `any`.

### 2. Server Components

Gunakan Next.js App Router. Default ke server component. Gunakan `"use client"` hanya jika perlu interaktivitas.

### 3. API Client

Semua panggilan API harus melalui `lib/api.ts`. Jangan panggil fetch langsung di komponen.

### 4. Styling

Gunakan Tailwind CSS utility classes. Jangan buat file CSS terpisah untuk satu komponen sederhana.

---

## Aturan Git dan Commit

### 1. Branch Naming

```
feature/nama-fitur
fix/nama-bug
refactor/nama-refactor
docs/nama-dokumen
```

### 2. Commit Messages

Gunakan conventional commits:

```
feat: Tambah endpoint unified signal
fix: Perbaiki error handling di data collector
refactor: Pindahkan indikator ke package terpisah
docs: Update API specification
chore: Update dependencies
```

### 3. Jangan Commit

Jangan commit file berikut:
- `.env` (environment variables)
- `__pycache__/`
- `.venv/`
- `node_modules/`
- File binary besar
- Celery beat schedule database
- File IDE (`.vscode/`, `.idea/`)

---

## Aturan Review

Sebelum menganggap task selesai, AI agent harus:

1. **Verifikasi sintaks:** Pastikan kode tidak memiliki syntax error
2. **Cek import:** Pastikan semua import valid dan tidak circular
3. **Cek tipe:** Pastikan type hints konsisten
4. **Cek async/sync:** Pastikan async function dipanggil dengan `await`
5. **Cek error handling:** Pastikan error ditangani dengan tepat

---

## Catatan Khusus

### 1. Celery dan Async

Celery task tidak bisa langsung async. Untuk async operations di Celery, gunakan `asyncio.run()`:

```python
@shared_task(name="task_name")
def my_task(self):
    import asyncio
    return asyncio.run(_async_function())
```

### 2. Circular Imports

Hindari circular imports dengan:
- Menempatkan import di dalam fungsi (lazy import)
- Memisahkan type definitions ke file terpisah
- Menggunakan `TYPE_CHECKING` untuk type hints

### 3. Global State

Paper trading dan MT5 bridge menggunakan global state (in-memory). Untuk production, ini harus dipindahkan ke database atau Redis.

### 4. Environment Variables

Semua konfigurasi diakses melalui `al_syaka_common.config.settings`. Jangan akses `os.environ` langsung.
