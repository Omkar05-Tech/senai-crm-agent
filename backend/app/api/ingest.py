from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.email import EmailPayload
from app.models.schema import Email, Thread, Contact

router = APIRouter()

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_email(payload: EmailPayload, db: Session = Depends(get_db)):
    # 1. Deduplication Safety-Valve: If message_id exists, return 200 OK without duplication
    existing_email = db.query(Email).filter(Email.message_id == payload.message_id).first()
    if existing_email:
        return {"status": "ignored", "detail": "Duplicate message_id captured. Idempotency enforced."}

    # 2. Contact Sync: Establish contact record shell if sender is unknown
    contact = db.query(Contact).filter(Contact.email == payload.sender).first()
    if not contact:
        contact = Contact(email=payload.sender, status="Active")
        db.add(contact)
        db.flush() 

    # 3. Thread Orchestration: Link structural timeline to existing id or spawn new thread state
    thread = db.query(Thread).filter(Thread.thread_id == payload.thread_id).first()
    if not thread:
        thread = Thread(
            thread_id=payload.thread_id,
            subject=payload.subject if payload.subject else "No Subject Specified",
            sender_email=payload.sender,
            status="Open"
        )
        db.add(thread)
        db.flush()

    # 4. Save clean data safely within current transaction boundary
    new_email = Email(
        thread_id=thread.thread_id,
        message_id=payload.message_id,
        sender=payload.sender,
        subject=payload.subject,
        body=payload.body,
        timestamp=payload.timestamp,
        status="Received"
    )
    db.add(new_email)
    
    try:
        db.commit()
    except Exception as error_exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Database commit execution failure: {str(error_exception)}"
        )

    return {
        "status": "success", 
        "message_id": payload.message_id, 
        "job_id": f"job_{payload.message_id}"
    }