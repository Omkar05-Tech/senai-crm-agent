from fastapi import APIRouter, Depends, status, Body, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schema import Email, Thread, Contact
from app.agent.workflow import run_agent_loop # <-- Import your new loop engine

router = APIRouter()

# @router.delete("/test/clear-email/{message_id}", status_code=status.HTTP_200_OK)
# def clear_specific_email(message_id: str, db: Session = Depends(get_db)):
#     """
#     Deletes a specific email by its message_id so you can test 
#     re-ingesting the exact same payload.
#     """
#     # 1. Search for the target email record
#     email_record = db.query(Email).filter(Email.message_id == message_id).first()
    
#     if email_record:
#         # Save the thread reference before deleting
#         thread_id = email_record.thread_id
#         sender_email = email_record.sender
        
#         # 2. Delete the email
#         db.delete(email_record)
#         db.flush()
        
#         # 3. Clean up the parent Thread if no other emails remain in it
#         remaining_emails_in_thread = db.query(Email).filter(Email.thread_id == thread_id).count()
#         if remaining_emails_in_thread == 0:
#             thread_record = db.query(Thread).filter(Thread.thread_id == thread_id).first()
#             if thread_record:
#                 db.delete(thread_record)
                
#         # 4. Clean up the Contact if they have no other threads/emails left
#         remaining_emails_by_contact = db.query(Email).filter(Email.sender == sender_email).count()
#         if remaining_emails_by_contact == 0:
#             contact_record = db.query(Contact).filter(Contact.email == sender_email).first()
#             if contact_record:
#                 db.delete(contact_record)
                
#         db.commit()
#         return {"status": "success", "detail": f"Cleared email {message_id} and related empty structures."}
        
#     return {"status": "not_found", "detail": f"Email {message_id} does not exist in database."}


@router.delete("/test/reset-all", status_code=status.HTTP_200_OK)
def reset_testing_database(db: Session = Depends(get_db)):
    """
    Clears all rows from emails, threads, and contacts tables.
    Leaves your knowledge base policy chunks untouched!
    """
    try:
        # Delete orders matter because of Foreign Key relationships!
        db.query(Email).delete()
        db.query(Thread).delete()
        db.query(Contact).delete()
        db.commit()
        return {"status": "success", "detail": "Transactional testing tables wiped completely clean."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "detail": str(e)}
    


@router.post("/test/run-agent", tags=["Development Utilities"])
def test_agent_execution(
    email_body: str = Body(..., embed=True),
    thread_id: str = Body("test_debug_thread", embed=True),
    db: Session = Depends(get_db)
):
    """
    Development endpoint to manually force the ReAct agent to process an email text.
    Returns the complete Chain-of-Thought execution trace (Thought -> Action -> Observation).
    """
    try:
        # Run the autonomous execution loop
        result = run_agent_loop(
            email_body=email_body,
            thread_id=thread_id,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent runtime crash: {str(e)}")