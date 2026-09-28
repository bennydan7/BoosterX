# BoostX System Operations Runbook

This document serves as the primary operational guide for managing and maintaining the BoostX platform in production.

---

## 1. System Architecture Overview

BoostX consists of:
1. **Flask 3 Web Application**: Serves the REST API and frozen React SPA frontend from `dist/`.
2. **SQLite / PostgreSQL Database**: Core datastore for users, sessions, orders, payments, ledger, and system settings.
3. **Redis & RQ Worker Queue**: Handles background service catalog syncing, provider status polling, payment expiration, and session cleanup.
4. **Fulfillment Provider Adapter**: Interacts defensively with `boostcenter2.com/api/v2`.
5. **OpenAI Vision Client**: Processes uploaded payment screenshots and extracts transaction details.

---

## 2. Database Backup & Recovery

### Backup (SQLite Production File)
```bash
sqlite3 backend/boostx.db ".backup 'backend/backups/boostx_backup_$(date +%Y%m%d_%H%M%S).db'"
```

### Restoration
1. Stop Web and Worker processes:
   ```bash
   docker-compose down
   ```
2. Copy backup file over `backend/boostx.db`:
   ```bash
   cp backend/backups/boostx_backup_YYYYMMDD_HHMMSS.db backend/boostx.db
   ```
3. Restart application:
   ```bash
   docker-compose up -d
   ```

---

## 3. Provider API Key Rotation

If the provider API key is compromised or needs scheduled rotation:
1. Obtain the new key from `boostcenter2.com`.
2. Update `.env` or cloud secret environment variable:
   ```bash
   PROVIDER_API_KEY=new_provider_key_here
   ```
3. Run provider smoke test to verify connectivity:
   ```bash
   python scripts/provider_smoke.py --url https://boostcenter2.com/api/v2 --key new_provider_key_here --mode live
   ```
4. Restart web and worker containers.

---

## 4. Background Workers & Queue Monitoring

### Monitoring RQ Jobs
Inspect worker logs:
```bash
docker-compose logs -f worker
```

To run manual background tasks on demand from CLI:
- **Service Sync**: `python -c "from backend.app import create_app; from backend.app.workers.sync_services import sync_services_worker; app=create_app(); sync_services_worker(app)"`
- **Order Status Check**: `python -c "from backend.app import create_app; from backend.app.workers.order_worker import check_pending_orders; app=create_app(); check_pending_orders(app)"`
- **Payment Expiration**: `python -c "from backend.app import create_app; from backend.app.workers.order_worker import expire_payments; app=create_app(); expire_payments(app)"`

---

## 5. Ledger & Payment Exception Handling

### Resolving Payment Reviews (Ambiguous AI Verification)
1. Log into the Admin Panel at `#/admin-payments`.
2. Locate payments marked with status `Review Required` or `Verifying`.
3. Click **Review** to inspect the uploaded screenshot alongside the AI-extracted fields (detected amount, reference, recipient).
4. **Approve**: If the screenshot shows a valid payment to `0202979378` (BOOSTX), click **Approve Payment**. This creates a posted `PAYMENT_CREDIT` transaction on the owner's ledger.
5. **Reject**: If the screenshot is invalid, duplicate, or underpaid, click **Reject Payment** and enter a customer-facing rejection reason.

### Resolving Ambiguous Provider Orders (`needs_attention=True`)
1. Log into `#/admin-orders` and filter by `Needs Attention`.
2. For orders where a provider timeout occurred:
   - Check `boostcenter2.com` panel to see if the order was received.
   - If received, click **Mark Submitted** and enter the provider order ID.
   - If not received, click **Release** to return the reserved debit to the customer's balance.

---

## 6. AI Vision Prompt & Threshold Calibration

The AI payment vision extractor lives in `backend/app/ai/payment_ai.py`.
- **System Prompt Calibration**: Edits to the vision extraction prompt should be tested against sample receipts in `backend/tests/fixtures/`.
- **Confidence Threshold**: The decision engine in `backend/app/payments/decision_engine.py` flags payments with confidence < 0.85 for manual review.
