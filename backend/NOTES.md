# Starter modules (from the BoostX chat)

Drop this `backend/` folder into the repo root, then run the finish prompt.

Known changes the prompt will make to these files:
1. providers/provider_client.py: never retry `add`, `cancel`, `refill` (retrying `add` can create duplicate provider orders).
2. orders/claim_service.py: guest money follows the current browser's guest session; contact-based claiming moves orders only and is off by default.
3. auth/*: swap InMemoryUserRepository for a SQLAlchemy repository; normalize phones to E.164; add full_name.
