# 🚀 SoMailer: Smart Email Intelligence — Master Handoff Document

## 📌 Project Overview
**SoMailer** is an enterprise-grade AI email orchestration system designed to transform raw inbox noise into structured operational intelligence. It uses a **Multi-Agent LangGraph Brain** to classify, summarize, and prioritize emails, feeding a premium real-time dashboard for management oversight.

### 🎯 Core Vision
Building a system where emails aren't just read, but **understood** and **acted upon** automatically. The goal is to move from a manual "triaging" mindset to an "automated executive assistant" model.

---

## 🏗️ Technical Architecture

### 1. Infrastructure (Containerized)
*   **Database**: PostgreSQL 16 with `pgvector` for semantic search capabilities.
*   **Cache/State**: Redis 7 for task queuing and future stateful agent interactions.
*   **Workflow Engine**: n8n (Local Docker instance) for raw data ingestion and outward integrations.

### 2. The Brain Layer (FastAPI + LangGraph)
Located in `/backend/app/`, this is the agentic heart of the system.
*   **Graph Orchestrator**: `graph.py` defines a linear-to-conditional flow:
    *   **START** -> `identity_node` -> `classification_node`.
    *   **Conditional Split**: `should_research` checks the category. If `FYI_Read` or `Cold_Outreach`, it skips to `planner_node`. Otherwise, it routes through `researcher_node`.
    *   `researcher_node` -> `planner_node` -> **END**.
*   **Nodes**:
    *   `identity_agent.py`: Matches senders against `user_registry.csv` (Columns: `full_name`, `corporate_email`, `department`, `manager_email`, `priority_projects`, `working_hours`, `no_interrupt_list`).
    *   `classifier_agent.py`: Uses `llama-3.3-70b-versatile` with a strict JSON system prompt.
    *   `researcher_agent.py`: Currently mocks project constraints; ready for `pgvector` integration.
    *   `planner_agent.py`: Maps 5 distinct categories to 5 specific n8n actions (`trigger_incident`, `propose_times`, `draft_task`, `archive_or_notify`, `spam_filter`).
    *   `dispatcher.py`: POSTs to `N8N_WEBHOOK_URL` (configurable in `.env`).

### 3. The Display Layer (React 19 + Vite 8)
Located in `/frontend/`, designed for high-resolution intelligence monitoring.
*   **Component Architecture**:
    *   `App.jsx`: Global shell and root navigation. Implements an **8000ms system ping** to monitor backend connectivity.
    *   `CommandCenter.jsx`: Displays a live system health grid (Brain, Gateway, Database, Queue).
    *   `IntelligenceFeed.jsx`: The primary data grid. Features a **Detail Slide-Over** (`EmailDetail`) for deep inspection of AI classifications and Vision insights.
    *   `Sidebar.jsx`: Navigation and **Universal Theme Toggle**.
    *   `ThemeContext.jsx`: Manages `Obsidian` vs. `Pearl` mode using CSS class toggles on `document.documentElement`.
*   **Data Sync**: `useEmails.js` hook implements a **5000ms polling interval** using `axios` to fetch the latest 50 signals.
*   **Design System**: Tailwind CSS v4 `@theme` logic located in `src/index.css`. Uses Inter for typography and Framer Motion for staggered list entrance animations.

---

## 🔀 Data Pipeline (n8n Webhooks)

### Migration Workflow
Used for "rehydrating" the system with historical data.
*   **Logic**: Fetches 50 most recent emails, cleans them using a **Format-Agnostic JavaScript Code Node**, and batches them to the FastAPI `/process-email` gateway.
*   **Key Fix**: The code now robustly handles both `Simplified` and `Complete` Gmail formats, ensuring `from` and `subject` fields are never "unknown."

### Vision Main Automation
The live trigger for new incoming mail.
*   **Attachment Handling**: If an image or PDF is detected, it is sent to **Groq/Llama Vision** capability. The resulting text analysis is appended to the payload passed to the Backend.

---

## ✅ Milestones Reached (This Session)
1.  **High-Fidelity Migration**: Fixed the B64 decoding and header parsing logic in n8n.
2.  **Brain Un-Mocking**: Removed all hardcoded fallback responses. 
3.  **Model Upgrade**: Transitioned from Gemini API to **Groq's Llama 3.3 70B** model for better performance and cost efficiency.
4.  **Backend Robustness**: Fixed a critical crash where the system couldn't handle "list" typed responses from the LLM.
5.  **Persistence Layer**: Implemented a `TRUNCATE` procedure to clear prototype data and verify new high-fidelity records.
6.  **Premium UI Fixes**: Restructured `index.css` to solve PostCSS import order warnings and improved the Intelligence Panel visibility.

---

## 🚦 State of the Union (For the New Agent)
*   **Backend URL**: `http://localhost:8000`
*   **Frontend URL**: `http://localhost:5173`
*   **Database**: `email_intelligence` on port 5432.
*   **Current Blocker**: None. The pipeline is "Green."
*   **Registry**: The `user_registry.csv` in `backend/data/` defines the VIPs. Update this to test the Identity Agent properly.

---

## 📦 Full Dependency List

### Backend (Python 3.10+)
*   `fastapi`, `uvicorn`: API Gateway & Web Server.
*   `langchain`, `langgraph`: Multi-agent orchestration framework.
*   `langchain-groq`: Brain engine (Using `Llama 3.3 70B` model).
*   `psycopg2-binary`: PostgreSQL adapter for persistence.
*   `pandas`: Registry handling for corporate identity.
*   `python-dotenv`: Environment variable management.
*   `redis`: Cache and future distributed task state.

### Frontend (React 19 + Vite 8)
*   `tailwindcss` (v4): Design system and styling.
*   `framer-motion`: UI animations and staggered feed transitions.
*   `axios`: HTTP client for intelligence polling.
*   `lucide-react`: Iconography.

---

## 🛠️ Operating Procedures

### Starting the Project
```powershell
# 1. Start Containers (DB & Redis)
docker-compose up -d

# 2. Start Backend (from /backend)
# Root activation: .\venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start Frontend (from /frontend)
npm run dev
```

### Infrastructure Persistence
*   **Database**: `postgres_data` volume ensures email logs survive container restarts.
*   **Redis**: `redis_data` volume preserves session history.
*   **n8n**: Configured to run on port `5678`.

---

## 🔮 Future Roadmap (Upcoming Steps)
1.  **Phase 4: RAG Integration**:
    *   Connect the `researcher_agent.py` to `pgvector`.
    *   Store company policies and past project briefs to allow the AI to answer "How should I reply to this based on our policy?"
2.  **Phase 5: Analytics & KPIs**:
    *   Build the "Analytics" tab in the dashboard.
    *   Visualize response times, urgency trends, and "time saved" by the AI.
3.  **Phase 6: Deployment & Security**:
    *   Move from `localhost` to environment variables.
    *   Implement JWT authentication for the dashboard.

---

**End of Handoff.** Use this as your context foundation and understanding the whole project.
