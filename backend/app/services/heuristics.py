import re

def run_heuristic_pre_filter(body: str, subject: str, sender: str) -> dict:
    """
    Layer 1 Intelligence: Sub-10ms regex scanning to save LLM costs and route immediate threats.
    Returns a predefined AI profile if a strict heuristic is hit, else returns None.
    """
    text = (subject + " " + body).lower()
    
    # 1. Internal Routing (@internal.com, @mycompany.com)
    if "@internal.com" in sender or "@mycompany.com" in sender:
        return {"category": "Internal", "urgency": "Low", "requires_human": False, "confidence": 1.0, "reasoning": "Internal domain detected."}

    # 2. Security & Ransomware Flags (Highest Priority)
    security_keywords = ['ransomware', 'breach', 'btc', 'bitcoin', 'hacked', 'stolen data']
    if any(word in text for word in security_keywords):
        return {"category": "Security", "urgency": "Critical", "requires_human": True, "confidence": 1.0, "reasoning": "Security threat/ransomware heuristic triggered."}

    # 3. Fast Urgency/Legal Flags
    urgent_keywords = ['urgent', 'p0', 'legal', 'cease and desist', 'lawsuit', 'sue', 'gdpr', 'article 20']
    if any(word in text for word in urgent_keywords):
        return {"category": "Legal", "urgency": "High", "requires_human": True, "confidence": 1.0, "reasoning": "Legal/Urgent heuristic triggered."}

    # 4. Spam Detection
    spam_keywords = ['nigerian prince', 'seo pitch', 'buy followers', 'guaranteed ROI', 'unsubscribe']
    if any(word in text for word in spam_keywords):
        return {"category": "Spam", "urgency": "Low", "requires_human": False, "confidence": 0.95, "reasoning": "Spam keyword detected."}

    # If no strict heuristics match, return None to pass it to Layer 2 (Gemini LLM)
    return None