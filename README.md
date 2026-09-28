# BoostX — Ghana Social Media Panel (GHS Only)

BoostX is a guest-checkout social media boosting panel built specifically for Ghana, supporting local Mobile Money payments in Ghana Cedi (GHS) only.

---

## Features

- **Guest Checkout & Cookie Sessioning**: Customers can browse, fund their wallet, place orders, and track fulfillment without registering an account.
- **Mobile Money & AI Vision Verification**: Integrates Telecel Cash, MTN MoMo, and AirtelTigo Cash payments with OpenAI Vision verification for instant receipt verification.
- **Double-Entry Financial Ledger**: Single-transaction atomic balance locking (`posted`, `reserved`, `released`) preventing double-spend and negative balances.
- **Defensive Provider Integration**: Wrapped SMM panel API integration (`boostcenter2.com/api/v2`) with zero-retry guarantees on state-changing actions (`add`, `cancel`, `refill`).
- **Comprehensive Admin Panel**: Full management dashboard for payment reviews, order fulfillment, catalog controls, exchange rates, audit logs, and system health.
- **Frozen Frontend**: React 19 + Tailwind v4 single-page application with hash routing and lazy-loaded admin screens.

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
│   │   └── workers/        # Background workers & status polling
│   ├── tests/              # Pytest test suite (M1 to M6)
│   ├── cli.py              # CLI seed & create-admin commands
│   └── config.py           # System constants & operational limits
├── src/                    # Frozen React SPA frontend
│   ├── api/                # Typed REST API client
│   ├── components/         # Missing spec screens & lazy admin screens
│   └── App.tsx             # Main router & layout shell
├── docs/                   # Implementation plan, runbook, decisions & deviations
├── scripts/                # Provider smoke test CLI tool
├── docker-compose.yml      # Container orchestration (Web, Worker, Redis)
└── render.yaml             # Render deployment blueprint
```

---

## Quickstart & Local Setup

### 1. Requirements
- Python 3.12+
- Node.js 18+

### 2. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Backend Setup & Pytest
```bash
pip install -r backend/requirements.txt
python -m pytest backend/tests
```

### 4. Seed Database & Create Admin
```bash
flask --app backend.app seed
```

### 5. Frontend Build
```bash
npm install
npm run build
```

### 6. Run Application Server
```bash
python -m backend.app.cli seed
python -c "from backend.app import create_app; app = create_app(); app.run(port=5000)"
```

---

## Testing & Verification

Run the full pytest suite:
```bash
python -m pytest backend/tests
```

Run the provider smoke test CLI:
```bash
python scripts/provider_smoke.py --mode fake
```

---

## Deployment

Deploy using Docker Compose:
```bash
docker-compose up --build -d
```

Or deploy to Render using `render.yaml`.
