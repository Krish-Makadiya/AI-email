from typing import Dict, Any
from app.registry_loader import load_user_registry
from app.agent_state import GraphState

def process_identity(state: GraphState) -> Dict[str, Any]:
    """Identity Node: Matches sender against user registry to determine classification."""
    email_data = state.get("email_data", {})
    sender = email_data.get("sender", "")
    receiver = email_data.get("receiver", "")

    try:
        registry_df = load_user_registry()
    except Exception as e:
        registry_df = None
    
    classification = "Team"
    user_info = {}
    
    if registry_df is not None and not registry_df.empty:
        # Find receiver in registry
        user_row = registry_df[registry_df["corporate_email"] == receiver]
        if not user_row.empty:
            user_info = user_row.iloc[0].to_dict()
            manager_email = user_info.get("manager_email", "")
            # If the sender is their manager or it's flagged as 1-on-1
            if sender == manager_email or email_data.get("is_1on1", False):
                classification = "Individual"
                
    # Basic fallback heuristic if not matching registry explicitly
    elif email_data.get("is_1on1", False):
        classification = "Individual"

    # Signature Logic: Student vs Developer
    domain = sender.split('@')[-1].lower() if '@' in sender else ""
    is_edu = domain.endswith('.edu') or "university" in sender.lower() or "college" in sender.lower()
    
    signature_type = "Student" if is_edu else "Developer"
    
    # Custom signatures
    signatures = {
        "Student": f"Best regards,\n{state.get('user_info', {}).get('name', 'Tanishq')}\nComputer Science Candidate",
        "Developer": f"Regards,\n{state.get('user_info', {}).get('name', 'Tanishq')}\nFull-Stack AI Engineer | SoMailer Dev"
    }
    
    user_info['signature'] = signatures.get(signature_type)
    user_info['identity_type'] = signature_type

    # Merge registry info with existing profile info
    final_user_info = state.get("user_info", {}).copy()
    final_user_info.update(user_info)

    return {"classification": classification, "user_info": final_user_info}
