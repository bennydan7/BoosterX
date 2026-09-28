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
