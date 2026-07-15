### Al-Syaka Quant AI

# AI-powered Market Intelligence & Trading Signal Platform

## Quick Start

### Prerequisites

- Python >= 3.11
- Node.js >= 18
- pnpm >= 9
- Docker & Docker Compose

### 1. Start Infrastructure

```bash
docker compose -f docker/docker-compose.yml up -d
```

### 2. Setup Python Environment

```bash
# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync all Python packages
uv sync
```

### 3. Setup Frontend

```bash
pnpm install
```

### 4. Run Database Migrations

```bash
cd apps/api
uv run alembic upgrade head
```

### 5. Start Development

```bash
# Start API server
cd apps/api && uv run uvicorn src.main:app --reload

# Start Celery worker (in another terminal)
cd apps/api && uv run celery -A src.celery_app worker --loglevel=info

# Start Celery beat scheduler (in another terminal)
cd apps/api && uv run celery -A src.celery_app beat --loglevel=info

# Start Dashboard (in another terminal)
cd apps/dashboard && pnpm dev
```

### 6. Access

- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Dashboard: http://localhost:3000

## Project Structure

\`\`\`
al-syaka-quant-ai/
├── apps/
│   ├── api/                  # FastAPI backend
│   ├── dashboard/            # NextJS frontend
│   ├── ai-engine/            # AI model training & inference
│   ├── backtester/           # Backtesting engine
│   ├── signal-service/       # Signal generation
│   └── mt5-bridge/           # MT5 connector
├── packages/
│   ├── common/               # Shared utilities & models
│   ├── indicators/           # Technical indicators
│   ├── feature-engineering/  # Feature extraction
│   ├── quant/                # Quantitative analysis
│   └── risk/                 # Risk management
├── database/                 # Migrations & seed data
├── docker/                   # Docker Compose
└── .github/                  # CI/CD
\`\`\`
