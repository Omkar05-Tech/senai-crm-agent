from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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

@router.get("/stats")
def get_analytics_stats(db: Session = Depends(get_db)):
    """Calculates AI performance metrics for the Analytics Dashboard."""
    
    # Total emails processed
    total_emails = db.query(Email).count()
    
    if total_emails == 0:
        return {"total": 0, "escalated": 0, "avg_sentiment": 0, "categories": []}

    # Total emails escalated to a human
    escalated_count = db.query(Email).filter(Email.requires_human == True).count()
    
    # Average sentiment score
    avg_sentiment = db.query(func.avg(Email.sentiment_score)).scalar() or 0

    # Group by category for the pie chart
    category_counts = db.query(
        Email.category, func.count(Email.id)
    ).group_by(Email.category).all()

    # Format the data for React and Recharts
    categories = [{"name": cat or "Unknown", "value": count} for cat, count in category_counts]

    return {
        "total": total_emails,
        "escalated": escalated_count,
        "escalation_rate": round((escalated_count / total_emails) * 100, 1),
        "avg_sentiment": round(avg_sentiment, 2),
        "categories": categories
    }