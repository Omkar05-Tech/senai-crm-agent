import re
from typing import Dict, Any

# We pre-compile our keyword lists so Python can search text instantly.
CRITICAL_PATTERNS = {
    # Matches words associated with security breaches and hackers
    "security": re.compile(r"\b(ransomware|hacked|breach|malware|compromised|suspicious login)\b", re.IGNORECASE),
    # Matches words indicating the customer is taking legal action
    "legal": re.compile(r"\b(lawyer|legal|sue|lawsuit|subpoena|gdpr|compliance|regulatory|court)\b", re.IGNORECASE),
    # Matches words showing the system is offline and losing money
    "outage": re.compile(r"\b(down|outage|crash|offline|broken|404|500 error|not responding)\b", re.IGNORECASE)
}

def run_heuristic_pre_filter(body: str, subject: str) -> Dict[str, Any]:
    """
    Scans the email for emergency keywords. 
    If a match is found, it forces a strict output so the LLM doesn't have to guess.
    """
    combined_text = f"{subject} {body}"
    
    # 1. Check for Hackers/Security threats first (Highest Priority)
    if CRITICAL_PATTERNS["security"].search(combined_text):
        return {
            "urgency": "Critical",
            "category": "Security Incident",
            "requires_human": True, # NEVER let AI auto-reply to hackers
            "confidence": 1.0
        }
        
    # 2. Check for Legal/GDPR threats next
    if CRITICAL_PATTERNS["legal"].search(combined_text):
        return {
            "urgency": "High",
            "category": "Legal & Compliance",
            "requires_human": True,
            "confidence": 1.0
        }
        
    # 3. Check for Server Outages
    if CRITICAL_PATTERNS["outage"].search(combined_text):
        return {
            "urgency": "Critical",
            "category": "Technical Support",
            "requires_human": True,
            "confidence": 0.9
        }
        
    # Return None if no emergency words are found, letting the LLM take over
    return None