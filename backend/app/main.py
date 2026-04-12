from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
import os

from app.graph import graph_app
from app.agent_state import GraphState
from app.dispatcher import dispatch_command
from dotenv import load_dotenv

load_dotenv() # Load variables from .env

app = FastAPI(title="Smart Email Assistant Gateway", version="1.0.0")

# Enable CORS for frontend dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/email_intelligence")

class EmailInput(BaseModel):
    sender_email: str
    subject: str
    content: str
    is_1on1: bool = False
    attachment_analysis: str = ""

@app.post("/process-email")
def process_email_endpoint(email: EmailInput, background_tasks: BackgroundTasks):
    """
    Receives raw email data (e.g. from n8n), triggers the LangGraph brain,
    and returns the formulated command_package.
    """
    # Map 'content' to 'body' for the brain nodes
    email_dict = email.model_dump()
    email_payload = {
        "sender": email_dict.get("sender_email"),
        "receiver": "user@corporate.com",
        "subject": email_dict.get("subject"),
        "body": email_dict.get("content"),
        "is_1on1": email_dict.get("is_1on1", False),
        "attachment_analysis": email_dict.get("attachment_analysis", "")
    }

    initial_state = GraphState(
        email_data=email_payload,
        user_info={},
        classification=None,
        category=None,
        urgency_score=None,
        short_summary=None,
        context=[],
        command_package={}
    )
    
    print("\n[Gateway] Triggering Graph Invocation...")
    result = graph_app.invoke(initial_state)
    cmd_package = result.get('command_package', {"action": "fallback", "payload": {}})
    background_tasks.add_task(dispatch_command, cmd_package)

    # Persistence: Save the transaction to the dashboard table
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Merge email input with the brain's classification
        dashboard_data = email.model_dump()
        dashboard_data['classification'] = result.get('classification', 'FYI_Read')
        dashboard_data['urgency_score'] = result.get('urgency_score', 0)
        
        import json
        cursor.execute(
            "INSERT INTO email_actions (payload) VALUES (%s)", 
            (json.dumps(dashboard_data),)
        )
        conn.commit()
    except Exception as e:
        print(f"DB Insert error: {e}")
    finally:
        if 'conn' in locals(): conn.close()
    
    return {
        "status": "success",
        "command_package": cmd_package
    }

@app.get("/process-email")
def get_processed_emails():
    """
    Fetches the last 50 processed emails from the email_actions table for the Dashboard.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM email_actions ORDER BY created_at DESC LIMIT 50")
        rows = cursor.fetchall()
        
        # Format for dashboard
        formatted_emails = []
        for row in rows:
            p = row['payload']
            formatted_emails.append({
                "id": row['id'],
                "sender_email": p.get('sender_email', 'unknown@corp.com'),
                "subject": p.get('subject', 'No Subject'),
                "content": p.get('content', ''),
                "classification": p.get('classification', 'FYI_Read'),
                "attachment_analysis": p.get('attachment_analysis', ''),
                "urgency_score": p.get('urgency_score', 0),
                "timestamp": row['created_at'].isoformat() if row['created_at'] else None
            })
            
        return {"emails": formatted_emails}
    except Exception as e:
        print(f"DB Fetch Error: {e}")
        return {"emails": []}
    finally:
        if 'conn' in locals(): conn.close()
