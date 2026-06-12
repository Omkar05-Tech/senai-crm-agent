from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import re

class EmailPayload(BaseModel):
    message_id: str
    sender: str
    subject: str = ""
    body: str = ""
    timestamp: datetime
    thread_id: str

    @field_validator('subject')
    @classmethod
    def clean_subject(cls, v: str) -> str:
        # Handle entirely empty subjects
        if not v or not v.strip():
            return "No Subject"
        return v.strip()

    @field_validator('body')
    @classmethod
    def clean_and_truncate_body(cls, v: str) -> str:
        # 1. Strip HTML tags (e.g., <p>, <br>) using regex
        clean_text = re.sub(r'<[^>]+>', '', v)
        
        # 2. Replace common HTML entities like &nbsp; with spaces
        clean_text = clean_text.replace('&nbsp;', ' ').strip()
        
        # 3. Handle entirely empty bodies (whitespace only)
        if not clean_text:
            return "[EMPTY BODY]"
            
        # 4. Truncate to 10,000 characters to protect the LLM context window
        if len(clean_text) > 10000:
            clean_text = clean_text[:10000] + "... [TRUNCATED BY SYSTEM LIMITS]"
            
        return clean_text