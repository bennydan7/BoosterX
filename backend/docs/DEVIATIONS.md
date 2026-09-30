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

### DEV-007: Admin Dashboard Design System Alignment Audit & Refactoring
- **File**: `frontend/src/components/AdminComponents.tsx`, `frontend/src/App.tsx`
- **Type**: Component Architecture & Design System Alignment.
- **Audit Findings**:
  - **Overview**: Used raw `<div style={{ marginTop: "1.5rem" }}>`, inline flex containers, and raw `<button className="btn">` elements instead of shared `<PageTitle>`, `<Card>`, `<Icon>`, and `<Button>` components.
  - **Payments & Payment Review**: Used raw `<input>` inside raw `<label className="field">`, raw `<button className="back-link">`, and inline margins/flex styles instead of `<Field>`, `<Button variant="ghost">`, `<Button variant="primary">`, and `<Status>`.
  - **Orders, Services, Platforms**: Used raw HTML buttons, inline flex containers (`display: "flex", gap: "0.5rem"`), and raw text statuses instead of `<Status>`, `<Button>`, and `.admin-order-actions` layout containers.
  - **Settings, Health, Audit**: Used raw `<dl>`, raw `<input>`, and inline margin styles instead of shared `<PageTitle>`, `<Card>`, `<Field>`, `<Status>`, and `<Button>` components.
  - **Shell Integration**: Admin screens previously bypassed `<Shell>`, missing sidebar navigation, top header, font inheritance, and shared layout scale. Wrapped admin screens in `<Shell>` with `adminNavGroups` so admin inherits the unified layout, font family, typography scale, icon set, and sidebar navigation while preserving the denser graphite internal-tool color palette.
- **Resolution**: Refactored all 8 admin screens (`AdminDashboard`, `AdminPayments`, `AdminPaymentReview`, `AdminOrders`, `AdminServices`, `AdminPlatforms`, `AdminConfigPage` audit/health/pricing) to consume shared UI primitives (`Card`, `Button`, `Field`, `PageTitle`, `Status`, `Icon`) and wrapped admin routes inside `<Shell>`.


