# BoostX Frontend & Design Deviations Log

This document records every deviation from original prototype files, detailing the file, line, and rationale to ensure compliance with the frozen design contract.

---

## Deviations Log

### DEV-001: Frontend API Client Layer Addition
- **File**: `src/api/client.ts`, `src/api/types.ts`
- **Type**: Addition of API client module.
- **Rationale**: Allowed per prompt contract §0 ("Allowed: Adding src/api/"). Provides typed API integration, CSRF handling, and same-origin fetch calls.

### DEV-002: Routing & Missing Spec Component Integration
- **File**: `src/App.tsx`
- **Type**: Hash routing parsing (`#/track`, `#/help`, `#/terms`, `#/privacy`, `#/refunds`, `#/cookies`, `#/security`, `#/disclaimer`, `#/404`), dynamic state wiring.
- **Rationale**: Connects hardcoded prototype pages to real API responses and renders missing spec required screens (guest order tracking, FAQ, legal disclosures, 404) using existing CSS classes without altering `src/index.css` or visual styling.

### DEV-003: Stale Payment Expiration Docstring Fix
- **File**: `backend/app/workers/order_worker.py`
- **Type**: Bugfix / Docstring Correction.
- **Rationale**: `expire_payments()` docstring incorrectly stated a "20-minute" window, whereas `Payment.expires_at` models and worker logic use 30 minutes per spec §10. Corrected comment to 30 minutes.

### DEV-004: Environment Variable Dual-Naming Harmonization
- **File**: `backend/app/config.py`, `.env.example`, `backend/app/ai/payment_ai.py`
- **Type**: Configuration Compatibility Fix.
- **Rationale**: Code originally checked `AI_API_KEY` and `AI_MODEL`, while `.env.example` documented `OPENAI_API_KEY` and `OPENAI_VISION_MODEL`. Config was updated with fallbacks to seamlessly accept both naming conventions without breaking deployment configs.

### DEV-005: Optional Figma Site Configuration Import Fallback
- **File**: `frontend/vite.config.ts`
- **Type**: Build System Fix.
- **Rationale**: Prototype `vite.config.ts` statically imported `./.figma/make/site.json`, which was missing in clean checkouts. Added a safe `fs.existsSync()` check to gracefully fall back to an empty object `{}` when the file is absent.

### DEV-006: Repository Structure Consolidation (`backend/` & `frontend/`)
- **File**: `backend/docs/`, `backend/scripts/`, `frontend/.figma/`, `frontend/.figaro/`
- **Type**: Directory Layout Consolidation.
- **Rationale**: Consolidated root loose directories using `git mv` so repo root contains strictly `frontend/` and `backend/` directories, alongside root orchestration configs (`README.md`, `Dockerfile`, `docker-compose.yml`, `render.yaml`, `.env.example`, `.gitignore`). `.figma/` and `.figaro/` moved into `frontend/` with `frontend/vite.config.ts` updated to load `frontend/.figma/make/site.json` directly.

