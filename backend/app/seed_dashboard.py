import json
import psycopg2
import random
from datetime import datetime, timedelta

DATABASE_URL = "postgresql://user:password@localhost:5432/email_intelligence"

SENDERS = [
    "jeff.bezos@amazon.com", "satya.nadella@microsoft.com", "sam.altman@openai.com",
    "elon.musk@x.com", "jensen.huang@nvidia.com", "v.buterin@ethereum.org",
    "finance@internal-corp.com", "legal@partner-firm.com", "hr@global-tech.io",
    "notifications@github.com", "security@aws.amazon.com", "ops@data-center.local"
]

SUBJECTS = [
    "Urgent: Infrastructure Scaling Requirements",
    "Re: Q3 Financial Audit Results",
    "Security Alert: Unusual Login Pattern",
    "Partnership Opportunity: AI Compute Cluster",
    "Action Required: Compliance Signature",
    "Internal: Team Performance Review",
    "Vision Analysis: Floor Plan for New HQ",
    "FYI: New API Documentation Released",
    "Urgent Fire: Production Database Latency",
    "Weekly Sync: Marketing Alpha Project",
    "Invoice #88219 - Pending Payment",
    "Technical Spec: Multi-Agent Orchestration"
]

CLASSIFICATIONS = [
    "Urgent_Fire", "Action_Required", "FYI_Read", "Individual", "Scheduling", "Action_Required", "FYI_Read"
]

ATTACHMENTS = [
    "Architectural diagram shows optimal node distribution. RAG throughput estimated at 2k tokens/sec.",
    "Invoice breakdown: $45,000 for H100 GPU compute credits. Verification recommended.",
    "Legal draft identifies 3 risk clauses regarding data sovereignty in EU regions.",
    "Floor plan analysis: Server room capacity can be increased by 20% with localized cooling.",
    "", "", "", "", "" # Most have no attachments
]

def seed():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        print("Cleaning old data...")
        cursor.execute("DELETE FROM email_actions")
        
        print("Seeding 50 intelligence signals...")
        for i in range(50):
            created_at = datetime.now() - timedelta(minutes=i * 15)
            sender = random.choice(SENDERS)
            subject = random.choice(SUBJECTS)
            classification = random.choice(CLASSIFICATIONS)
            attachment = random.choice(ATTACHMENTS)
            
            payload = {
                "sender_email": sender,
                "subject": f"{subject} [Batch {i}]",
                "content": f"Dear Team,\n\nThis is a signal processed via the LangGraph brain at {created_at.isoformat()}.\n\nThe intelligence layer has determined this requires {classification.replace('_', ' ')} logic.\n\nRegards,\nAI System",
                "classification": classification,
                "attachment_analysis": attachment,
                "urgency_score": random.randint(10, 95) if "Urgent" in classification else random.randint(0, 30)
            }
            
            cursor.execute(
                "INSERT INTO email_actions (payload, email_received_at, created_at) VALUES (%s, %s, %s)",
                (json.dumps(payload), created_at, created_at)
            )
            
        conn.commit()
        print("Done! 50 premium signals seeded.")
        
    except Exception as e:
        print(f"Seed failed: {e}")
    finally:
        if 'conn' in locals(): conn.close()

if __name__ == "__main__":
    seed()
