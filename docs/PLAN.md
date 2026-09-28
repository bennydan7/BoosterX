# BoostX Master Implementation Plan

This document maps every section of the BoostX MVP Build Specification (`src/imports/BoostX_MVP_Specification.pdf`) and Payment/Admin Correction Specification (`src/imports/BOOSTX_EXISTING_DESIGN___ADMIN___PAYMENT_CORRECTION.pdf`) to the files in the codebase implementing them across Milestones M1 through M8.

---

## Spec Section to File Mapping

### 1. System Vision & Architecture
- **Spec Section**: §1 System Architecture, §2 Principles, §3 Operational Limits
- **Implementation Files**:
  - `backend/app/config.py`: System constants, limits (GHS currency only, max 5 platforms, 10MB upload limit).
  - `docker-compose.yml`, `render.yaml`, `README.md`: Deployment architecture.

### 2. Database & Data Model (M1)
- **Spec Section**: §7 Database Schema, Prompt §3
- **Implementation Files**:
  - `backend/app/models/__init__.py`: SQLAlchemy ORM models.
  - `backend/app/models/user.py`: `users` model (E.164 phone normalization, notification_prefs, role, status).
  - `backend/app/models/guest.py`: `guest_sessions` model.
  - `backend/app/models/payment.py`: `payments`, `payment_verifications` models (`expires_at`, `attempt_count`, `rejection_reason`).
  - `backend/app/models/ledger.py`: `ledger_transactions` (posted, reserved, released).
  - `backend/app/models/order.py`: `orders`, `order_events`, `refills`, `refunds` (`idempotency_key`, `needs_attention`).
  - `backend/app/models/service.py`: `platforms`, `services` models.
  - `backend/app/models/support.py`: `support_tickets`, `support_messages` models.
  - `backend/app/models/system.py`: `settings`, `notifications`, `fraud_flags`, `admin_actions`.
  - `backend/migrations/`: Alembic database migrations.
  - `backend/app/cli.py`: Seed CLI command (`flask seed`, `flask create-admin`).

### 3. Authentication, Guest Sessions & Claiming (M2)
- **Spec Section**: §8 Auth & Accounts, §16 Guest Checkout, Prompt §4
- **Implementation Files**:
  - `backend/app/auth/models.py`, `backend/app/auth/auth_service.py`: User auth, lockout (5 attempts / 15 mins), generic errors.
  - `backend/app/auth/repository.py`: SQLAlchemy `UserRepository`.
  - `backend/app/auth/session.py`: HttpOnly signed cookie session manager (`session_version`, CSRF token).
  - `backend/app/auth/routes.py`: `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`.
  - `backend/app/orders/claim_service.py`: Guest session claiming on register/login (moves CURRENT guest session in 1 transaction; contact claiming disabled by default).
  - `backend/app/middleware.py`: Rate limiters, CSRF validation, Admin 404 guard (`/api/admin/*`).

### 4. Service Catalog, Pricing & Provider Sync (M3)
- **Spec Section**: §4 Platforms, §5 Catalog, §9 Pricing Engine, Prompt §5
- **Implementation Files**:
  - `backend/app/providers/provider_client.py`: `ProviderAdapter` (retry fixed: NO retry on `add`, `cancel`, `refill`).
  - `backend/app/providers/fake_provider.py`: `FakeProvider` for tests.
  - `backend/app/providers/interface.py`: `ProviderInterface`.
  - `backend/app/pricing/pricing_service.py`: `PricingService` with Decimal math (`customer_price = provider_cost * usd_to_ghs_rate + flat_markup_ghs`).
  - `backend/app/workers/sync_services.py`: Background worker sync, 5 platforms keyword mapping, default type filter.
  - `backend/app/workers/fx_worker.py`: FX rate auto-refresh worker with sanity band checks.
  - `backend/app/api/catalog.py`: GET `/api/platforms`, GET `/api/services`, GET `/api/services/:id`, POST `/api/orders/preview`.

### 5. Payments & AI Verification (M4)
- **Spec Section**: §10 Payment System, Prompt §6
- **Implementation Files**:
  - `backend/app/payments/routes.py`: POST `/api/payments`, POST `/api/payments/:id/screenshot`, GET `/api/payments/:id`, GET `/api/payments`.
  - `backend/app/payments/upload.py`: Magic byte check (PNG/JPEG/WEBP), Pillow re-encode to WEBP, 10MB limit, private file storage.
  - `backend/app/ai/payment_ai.py`: OpenAI-compatible vision client (`extract()`, pydantic validation, temperature 0).
  - `backend/app/payments/decision_engine.py`: Single-transaction verification, ledger credit insertion, `verified`/`rejected`/`review`/`expired` decision logic, `payment_recipient_aliases` matching.

### 6. Ledger, Orders & Background Workers (M5)
- **Spec Section**: §11 Order Lifecycle, §12 Ledger & Balance, Prompt §7
- **Implementation Files**:
  - `backend/app/services/ledger_service.py`: Single-transaction ledger calculator with `SELECT FOR UPDATE`.
  - `backend/app/orders/order_service.py`: `POST /api/orders` with idempotency, owner locking, provider submission outside DB lock, ambiguous failure handling (`needs_attention`).
  - `backend/app/orders/order_history_service.py`: Order listing, filtering, progress calculation.
  - `backend/app/workers/scheduler.py`: RQ worker & scheduler setup (`check_pending_orders`, `check_payment_status`, `process_refunds`, `expire_payments`, `cleanup_expired_sessions`).

### 7. Admin API & Management (M6)
- **Spec Section**: §13 Admin Capabilities, Correction Spec Section 2-10, Prompt §8
- **Implementation Files**:
  - `backend/app/admin/routes.py`: Dashboard overview stats, Payments management, Payment Review decision endpoints, Orders actions (track, cancel, refill, mark-submitted, release), Services toggle/patch/sync, Platforms toggle, Users list/suspend/activate, Transactions, Pricing, Provider balance & test connection, System health, Audit logs, Payment settings, Support tickets, POST `/api/admin/admins`.

### 8. Frontend Wiring & Missing Screens (M7)
- **Spec Section**: §15 Frontend Wiring, Prompt §9
- **Implementation Files**:
  - `src/api/client.ts`: Typed API client with same-origin fetch, CSRF header.
  - `src/api/types.ts`: TypeScript interfaces for all endpoints.
  - `src/App.tsx`: Hash routing (`#/dashboard`, `#/new-order`, `#/orders`, `#/order-details/:id`, `#/services`, `#/wallet`, `#/payment`, `#/transactions`, `#/support`, `#/profile`, `#/settings`, `#/admin`, `#/track`, `#/help`, `#/terms`, `#/privacy`, `#/refunds`, `#/cookies`, `#/security`, `#/disclaimer`, `#/404`), state replacement, lazy-loading admin screens (`React.lazy`), exact copy fixes.
  - `src/components/TrackOrder.tsx`, `src/components/HelpFAQ.tsx`, `src/components/LegalPages.tsx`, `src/components/NotFound.tsx`: Missing spec screens built strictly using existing components and CSS classes.

### 9. Tests, Security, Deployment & Documentation (M8)
- **Spec Section**: §14 Security, §17 Test Plan, §18 Environment & Config, Prompt §10, §11, §12
- **Implementation Files**:
  - `backend/tests/`: Pytest suite (concurrency lock tests, screenshot verification tests, idempotency, refund math, status mapping, security tests).
  - `scripts/provider_smoke.py`: Provider smoke test CLI tool.
  - `docs/DECISIONS.md`, `docs/DEVIATIONS.md`, `docs/RUNBOOK.md`, `README.md`.
