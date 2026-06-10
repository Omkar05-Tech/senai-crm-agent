from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class EmailPayload(BaseModel):
    message_id: str = Field(..., description="Unique message identification string")
    sender: str = Field(..., description="Sender electronic mail address identifier")
    subject: Optional[str] = ""
    body: Optional[str] = ""
    timestamp: datetime
    thread_id: str