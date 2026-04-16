# 🌐 SoMailer Project Continuation Map

This document serves as the handoff for the next session to ensure zero context loss.

## ✅ Accomplishments & Solved Issues

### 1. Intelligence Feed Stability
- **Issue**: Backend was crashing due to `NULL` payloads in individual rows (e.g., ID 301).
- **Fix**: Implemented a per-row `try/except` block in `main.py` fetch loop. The feed is now resilient to corrupted data.

### 2. Draft Hub UI Restoration
- **Issue**: "Full Blank Screen" when navigating to Drafts.
- **Fix**: Identified redundant `JSON.parse()` calls on already-parsed `suggested_slots` arrays in `Drafts.jsx`. Fixed the logic to handle both stringified and object formats safely.

### 3. Pipeline Synchronization (n8n ↔ Backend)
- **Host Routing**: Configured n8n (Docker) to reach the Windows host using `http://host.docker.internal:8000`.
- **Logic Fix**: Updated the `/email-actions/{id}/confirm` endpoint in `main.py` to correctly store `scheduled_time` and `google_event_id`.

---

## 🏗️ Current System State

| Component | Status | Address |
| :--- | :--- | :--- |
| **FastAPI Backend** | 🟢 RUNNING | `http://localhost:8000` |
| **React Frontend** | 🟢 RUNNING | `http://localhost:5173` |
| **n8n Container** | 🟢 RUNNING | `http://localhost:5678` |
| **PostgreSQL DB** | 🟢 RUNNING | `localhost:5432` |

- **Backend Process**: Running with `--reload` via Uvicorn.
- **Docker**: `n8ncontainer` is active and can ping `host.docker.internal`.
- **Credentials**: Google Calendar integration is active but needs verification.

---

## 🔴 PENDING: The "Invisible Lifecycle Cards" Issue

### The Problem
When the user clicks **"Confirm & Dispatch"** in the Draft Hub:
1. The draft disappears from the main list (Correct).
2. **The card DOES NOT appear in the Lifecycle Hub (sidebar).**
3. Database checks reveal the meetings remain in `New` status instead of moving to `Confirmed`.

### Debugging Progress
- **Confirmed**: 1 card (ID 99999) was manually repaired in the DB and shows up in the UI. 
- **The Gap**: New confirmations from the UI are **NOT reaching the database**.
- **Suspicion**: 
    - n8n's `Confirm Backend` node is failing to hit the `PATCH` endpoint.
    - OR the `Create Google Event` node is failing, terminating the workflow before it hits the backend.
- **Logs**: I have added a `requests.log` middleware to `main.py` to trace incoming traffic. Currently, no confirmation requests are seen in the log.

### Next Steps for the New Chat
1. **Trace n8n Execution**: Open n8n UI, trigger a confirmation, and check which node is failing (red dot).
2. **Verify `email_action_id`**: Ensure the ID passed from `Drafts.jsx` to n8n is correct.
3. **Log Check**: Run `check_drafts.py` to see if "Confirmation Drafts" are being generated. If they ARE, then `Confirm Backend` failed. If they ARE NOT, then `Create Google Event` failed.

---

## 🛠️ Utility Scripts Created
- `check_confirmed.py`: Lists all confirmed meetings in DB.
- `check_drafts.py`: Searches for "Confirmed" drafts.
- `repair_db.py`: Forces a timestamp onto NULL confirmed records.
- `requests.log`: Backend request logger (inside `/backend`).

---

**Ready to resume in the next session!**
