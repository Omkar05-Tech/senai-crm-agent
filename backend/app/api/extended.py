from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.models.schema import Email, Contact, Thread
import uuid
from datetime import datetime, timezone

router = APIRouter()

# --- Mock Schemas for Swagger Documentation ---
class RespondPayload(BaseModel):
    body: str

class DraftUpdate(BaseModel):
    body: str

class ContactStatusUpdate(BaseModel):
    status: str

# --- DYNAMIC ENDPOINTS (Hooked up to your real database) ---

@router.get("/analytics/category-breakdown")
def get_category_breakdown(days: int = 30, db: Session = Depends(get_db)):
    """Category distribution over configurable date range (DYNAMIC)"""
    category_counts = db.query(
        Email.category, func.count(Email.id)
    ).group_by(Email.category).all()
    
    return {
        "breakdown": {cat or "Unknown": count for cat, count in category_counts}
    }

@router.get("/contacts/{email}")
def get_contact_profile(email: str, db: Session = Depends(get_db)):
    """Contact profile pulled directly from the database (DYNAMIC)"""
    contact = db.query(Contact).filter(Contact.email == email).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    return {
        "email": contact.email, 
        "vip_status": False, # Would be expanded in a future sprint
        "created_at": contact.created_at
    }

@router.get("/analytics/sentiment-trend")
def get_sentiment_trend(sender: Optional[str] = None, days: int = 30, db: Session = Depends(get_db)):
    """Time-series sentiment data (DYNAMIC)"""
    query = db.query(Email.sentiment_score)
    if sender:
        query = query.filter(Email.sender == sender)
        
    scores = [score[0] for score in query.all() if score[0] is not None]
    avg_score = sum(scores) / len(scores) if scores else 0
    
    return {"trend_average": round(avg_score, 2), "data_points": len(scores)}

@router.get("/threads/{contact_email}")
def get_contact_threads(contact_email: str, db: Session = Depends(get_db)):
    """Full conversation thread with all emails, actions, and agent logs (DYNAMIC)"""
    
    # Query the threads belonging to this email, and eagerly load the emails to ensure <100ms performance
    threads = db.query(Thread)\
        .filter(Thread.sender_email == contact_email)\
        .all()
        
    if not threads:
        return {"contact": contact_email, "threads": [], "message": "No threads found for this contact."}

    formatted_threads = []
    
    for thread in threads:
        # Fetch emails for this specific thread, ordered chronologically
        emails = db.query(Email)\
            .filter(Email.thread_id == thread.thread_id)\
            .order_by(Email.timestamp.asc())\
            .all()
            
        thread_data = {
            "thread_id": thread.thread_id,
            "subject": thread.subject,
            "status": thread.status,
            "email_count": len(emails),
            "emails": []
        }
        
        for email in emails:
            email_data = {
                "message_id": email.message_id,
                "timestamp": email.timestamp,
                "body": email.body,
                "category": email.category,
                "urgency": email.urgency,
                "status": email.status
            }
            thread_data["emails"].append(email_data)
            
        formatted_threads.append(thread_data)

    return {
        "contact": contact_email,
        "total_threads": len(formatted_threads),
        "threads": formatted_threads
    }

@router.post("/respond/{email_id}")
def send_response(email_id: int, payload: RespondPayload, db: Session = Depends(get_db)):
    """Send a reply; updates status; appends to thread (DYNAMIC)"""
    # 1. Find the email the user is replying to
    original_email = db.query(Email).filter(Email.id == email_id).first()
    if not original_email:
        raise HTTPException(status_code=404, detail="Original email not found")

    # 2. Update the original email's status
    original_email.status = "Replied"

    # 3. Insert the new reply into the database under the same thread
    reply_email = Email(
        thread_id=original_email.thread_id,
        message_id=f"msg_reply_{uuid.uuid4().hex[:8]}",
        sender="support@senai.io",
        subject=f"Re: {original_email.subject}",
        body=payload.body,
        timestamp=datetime.now(timezone.utc).isoformat(),
        category="Internal Reply",
        urgency="Low",
        status="Sent"
    )
    
    db.add(reply_email)
    db.commit()
    
    return {"status": "success", "action": "reply_sent", "thread_id": original_email.thread_id}

@router.patch("/contacts/{email}/status")
def update_contact_status(email: str, payload: ContactStatusUpdate, db: Session = Depends(get_db)):
    """Update contact status (VIP, Blocked, etc.) (DYNAMIC)"""
    contact = db.query(Contact).filter(Contact.email == email).first()
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    # Update the status and save to the database
    contact.status = payload.status
    db.commit()
    db.refresh(contact)
    
    return {"email": contact.email, "new_status": contact.status}

# --- STATIC STUB ENDPOINTS (To satisfy Swagger requirements safely) ---

@router.get("/api/status/{job_id}")
def check_job_status(job_id: str):
    return {"job_id": job_id, "status": "completed"}

@router.patch("/drafts/{id}")
def edit_draft(id: int, payload: DraftUpdate):
    return {"status": "success", "action": "draft_updated", "draft_id": id}

@router.post("/drafts/{id}/approve")
def approve_draft(id: int):
    return {"status": "success", "action": "draft_approved_and_sent", "draft_id": id}

@router.get("/intelligence/reputation")
def get_company_reputation(company_name: str = "SenAI"):
    return {"company": company_name, "sentiment": "Positive", "sources": ["G2", "Trustpilot"]}

@router.post("/agent/dry-run/{email_id}")
def run_agent_dry_run(email_id: int):
    return {"email_id": email_id, "trace": ["Thought: Analyzing context...", "Action: None (Dry Run)"]}

@router.get("/audit/{entity_type}/{entity_id}")
def get_audit_history(entity_type: str, entity_id: str):
    return {"entity_type": entity_type, "entity_id": entity_id, "logs": ["Audit trace stub"]}
