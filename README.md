# BoostX — Ghana Social Media Panel (GHS Only)

BoostX is a guest-checkout social media boosting panel built specifically for Ghana, supporting local Mobile Money payments in Ghana Cedi (GHS) only.

---

## Features

- **Guest Checkout & Cookie Sessioning**: Customers can browse, fund their wallet, place orders, and track fulfillment without registering an account.
- **Mobile Money & AI Vision Verification**: Integrates Telecel Cash, MTN MoMo, and AirtelTigo Cash payments with OpenAI Vision verification for instant receipt verification.
- **Double-Entry Financial Ledger**: Single-transaction atomic balance locking (`posted`, `reserved`, `released`) preventing double-spend and negative balances under PostgreSQL row locks.
- **Defensive Provider Integration**: Wrapped SMM panel API integration (`boostcenter2.com/api/v2`) with zero-retry guarantees on state-changing actions (`add`, `cancel`, `refill`).
- **Comprehensive Admin Panel**: Full management dashboard for payment reviews, order fulfillment, catalog controls, exchange rates, audit logs, and system health.
- **Rate Limiting & Security Guards**: `Flask-Limiter` endpoint protection, generic 401 auth errors, 5-attempt lockout, and 404 security guard on `/api/admin/*`.

---

## Project Structure

```
BoosterX/
├── backend/
│   ├── app/
│   │   ├── admin/          # Admin REST API & security guard
│   │   ├── ai/             # OpenAI Vision receipt extraction
│   │   ├── api/            # Catalog, order, and account endpoints
│   │   ├── auth/           # Guest sessions, repository, user auth
│   │   ├── orders/         # 7-step order execution algorithm & refunds
│   │   ├── payments/       # Upload security & single-transaction decision engine
│   │   ├── pricing/        # Pricing engine (Decimal math, GHS conversion)
│   │   ├── providers/      # Defensive ProviderAdapter & FakeProvider
│   │   ├── services/       # Ledger balance calculator with row locking
│   │   └── workers/        # Background workers & scheduler
│   ├── migrations/         # Alembic database migrations
│   ├── tests/              # Pytest test suite (M1 to M6 + PostgreSQL concurrency tests)
│   ├── cli.py              # CLI seed & create-admin commands
│   ├── config.py           # System constants & operational limits
│   └── requirements.txt    # Python backend package dependencies
├── frontend/               # Frozen React 19 + Tailwind v4 frontend
│   ├── src/                # Typed REST API client, router, & screens
│   ├── package.json        # Frontend scripts & dependencies
│   └── vite.config.ts      # Vite config, outDir, & API proxy
├── docs/                   # Implementation plan, runbook, decisions & deviations
├── scripts/                # Provider smoke test CLI & secret scan script
├── Dockerfile              # Multi-stage production build (Node + Python + Gunicorn)
├── docker-compose.yml      # Container orchestration (Web, Worker, Postgres, Redis)
└── render.yaml             # Render deployment blueprint
```

---

## Quickstart & Local Setup

### 1. Requirements
- Python 3.12+
- Node.js 18+
- PostgreSQL 16+ (or SQLite for testing mode)

### 2. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Backend Setup & Migrations
```bash
pip install -r backend/requirements.txt
flask --app backend.app:create_app db upgrade
flask --app backend.app:create_app seed
flask --app backend.app:create_app create-admin
```

### 4. Frontend Build
```bash
cd frontend
npm ci
npm run build
cd ..
```

### 5. Run Application Server
```bash
python -m flask --app backend.app:create_app run --port 5000
```
Visit [http://localhost:5000/](http://localhost:5000/) in your browser.

---

## Testing & Verification

Run the full pytest suite (including PostgreSQL concurrency tests):
```bash
TESTING=true python -m pytest -v backend/tests
```

Run the provider smoke test CLI:
```bash
python scripts/provider_smoke.py --mode fake
```

Run secret leak build-scan:
```bash
python scripts/secret_scan.py
```

---

## Deployment

Deploy using Docker Compose with PostgreSQL & Redis:
```bash
docker-compose up --build -d
```

Or deploy to Render using `render.yaml`.
