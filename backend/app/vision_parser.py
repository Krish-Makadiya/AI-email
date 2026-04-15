"""
Vision Archive Parser: Converts raw Gemini vision output into structured actionable data.
This module extracts dates, financial figures, signatures, and action items from attachment analysis.
"""

import json
import re
from typing import Dict, Any, List

def parse_vision_analysis(raw_text: str) -> Dict[str, Any]:
    """
    Parse raw Gemini vision output into structured actionable data.
    
    Args:
        raw_text: Raw text output from Gemini 2.0 Flash document analysis
        
    Returns:
        Dictionary with structured fields: document_type, key_intelligence, critical_dates, 
        financial_figures, requested_action, and raw_text for fallback.
    """
    
    if not raw_text or raw_text.lower() in ['no attachment', 'none', '']:
        return {
            "document_type": "Unknown",
            "key_intelligence": [],
            "critical_dates": [],
            "financial_figures": [],
            "requested_action": "No actionable data found.",
            "raw_text": raw_text
        }
    
    result = {
        "document_type": "Document",
        "key_intelligence": [],
        "critical_dates": [],
        "financial_figures": [],
        "requested_action": "",
        "raw_text": raw_text
    }
    
    # Extract Document Type
    doc_type_match = re.search(r'Document Type:\s*([^\n]+)', raw_text, re.IGNORECASE)
    if doc_type_match:
        result["document_type"] = doc_type_match.group(1).strip()
    
    # Extract Key Intelligence
    key_intel_match = re.search(r'Key Intelligence:\s*([^\n]+(?:\n(?!Critical|Financial|Requested)[^\n]+)*)', raw_text, re.IGNORECASE)
    if key_intel_match:
        intel_text = key_intel_match.group(1).strip()
        # Split by bullet points or line breaks
        items = [item.strip() for item in re.split(r'[-•]\s+|\n', intel_text) if item.strip()]
        result["key_intelligence"] = items[:5]  # Limit to 5 items
    
    # Extract Critical Dates
    date_pattern = r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s+\d{4})?)\b'
    dates = re.findall(date_pattern, raw_text, re.IGNORECASE)
    result["critical_dates"] = list(set(dates))[:5]  # Unique dates, limit to 5
    
    # Extract Financial Figures
    financial_pattern = r'\$[\d,]+(?:\.\d{2})?|USD\s*[\d,]+(?:\.\d{2})?|Amount:\s*[\d,]+(?:\.\d{2})?'
    financials = re.findall(financial_pattern, raw_text, re.IGNORECASE)
    result["financial_figures"] = list(set(financials))[:5]  # Unique figures, limit to 5
    
    # Extract Requested Action
    action_match = re.search(r'(?:Requested Action|Next Step|Action Required):\s*([^\n]+(?:\n(?!Document Type|Key Intelligence|Critical|Financial)[^\n]+)*)', raw_text, re.IGNORECASE)
    if action_match:
        result["requested_action"] = action_match.group(1).strip()
    else:
        # Fallback: use the last sentence or first 100 chars
        sentences = re.split(r'[.!?]+', raw_text)
        if sentences:
            result["requested_action"] = sentences[-1].strip() or "Review document for actionable items."
    
    return result


def format_vision_card(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format parsed vision data into a card-ready structure for frontend rendering.
    
    Args:
        parsed_data: Output from parse_vision_analysis()
        
    Returns:
        Dictionary formatted for frontend Vision Archive cards
    """
    
    return {
        "type": parsed_data.get("document_type", "Document"),
        "intelligence": parsed_data.get("key_intelligence", []),
        "dates": parsed_data.get("critical_dates", []),
        "amounts": parsed_data.get("financial_figures", []),
        "action": parsed_data.get("requested_action", ""),
        "raw": parsed_data.get("raw_text", "")
    }


def batch_parse_emails(emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Parse attachment analysis for a batch of emails.
    
    Args:
        emails: List of email dictionaries with 'attachment_analysis' field
        
    Returns:
        List of emails with enhanced 'vision_data' field
    """
    
    for email in emails:
        if email.get("attachment_analysis"):
            parsed = parse_vision_analysis(email["attachment_analysis"])
            email["vision_data"] = format_vision_card(parsed)
        else:
            email["vision_data"] = None
    
    return emails


if __name__ == "__main__":
    # Test the parser with sample data
    sample_text = """
    Document Type: Invoice
    Key Intelligence: 
    - Payment due by April 30, 2026
    - Total amount: $5,400
    - Vendor: SoftwareCorp
    Critical Dates: 04/30/2026
    Financial Figures: $5,400
    Requested Action: Process payment and update accounting records.
    """
    
    parsed = parse_vision_analysis(sample_text)
    print(json.dumps(parsed, indent=2))
    
    card = format_vision_card(parsed)
    print("\nCard Format:")
    print(json.dumps(card, indent=2))
