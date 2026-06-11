from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schema import Email, Action

router = APIRouter()

@router.get("/inbox")
def get_all_emails(db: Session = Depends(get_db)):
    """Fetches all processed emails for the React sidebar."""
    emails = db.query(Email).order_by(Email.timestamp.desc()).all()
    return emails

@router.get("/logs/{email_id}")
def get_agent_logs(email_id: int, db: Session = Depends(get_db)):
    """Fetches the Chain-of-Thought reasoning logs for a specific email."""
    actions = db.query(Action).filter(Action.email_id == email_id).all()
    if not actions:
        return []
    return actions