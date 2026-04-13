from typing import Dict, Any
import json
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from app.agent_state import GraphState

def process_classification(state: GraphState) -> Dict[str, Any]:
    """Classifier Node: Categorizes email using Gemini API."""
    email_data = state.get("email_data", {})
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    
    api_key = os.environ.get("GEMINI_API_KEY", "your_api_key_here")
    
    # Use the latest supported model (gemini-2.0-flash)
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0, google_api_key=api_key)
    
    user_info = state.get("user_info", {})
    
    prompt = PromptTemplate.from_template(
        """You are the Principal Intelligence Agent for SoMailer.
Follow a strict Chain-of-Thought (CoT) reasoning path:

1. **Analyze Intent**: What does the sender want?
2. **Contextual Evaluation**: How does this relate to the user ({user_name})? 
   User's Daily Goal: {daily_goal}
3. **Drafting Strategy**: If this requires a response, should it be {tone}?
4. **Final Classification**: Categorize the email.

Email Subject: {subject}
Email Body: {body}
Attachment Analysis: {attachment}

Output a strictly valid JSON object with the following keys:
- "category": must be EXACTLY ONE of [Urgent_Fire, Scheduling, Action_Required, FYI_Read, Cold_Outreach]
- "urgency_score": integer from 1 to 10
- "short_summary": a 1-sentence summary of the actionable intelligence (dates, figures, or requests).

Output JSON Format {{"category": "...", "urgency_score": ..., "short_summary": "..."}} without markdown:"""
    )
    
    try:
        if api_key == "your_api_key_here":
            raise ValueError("GEMINI_API_KEY is not configured.")
        
        chain = prompt | llm
        response = chain.invoke({
            "subject": subject, 
            "body": body, 
            "attachment": email_data.get("attachment_analysis", "None"),
            "user_name": user_info.get("name", "User"),
            "daily_goal": user_info.get("daily_goal", "General email management"),
            "tone": user_info.get("tone_preference", "Professional")
        })
        
        text = str(response.content).strip()
    except Exception as e:
        print(f"LLM Error: {e}")
        # Return a conservative fallback that isn't hardcoded "Mocked" text
        return {
            "category": "FYI_Read",
            "urgency_score": 3,
            "short_summary": f"Automated processing note: {str(e)[:50]}..."
        }
    
    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM Response: {text}")
        result = {
            "category": "FYI_Read",
            "urgency_score": 1,
            "short_summary": "Failed to parse categorization."
        }
        
    return {
        "category": result.get("category", "FYI_Read"),
        "urgency_score": result.get("urgency_score", 1),
        "short_summary": result.get("short_summary", "")
    }
