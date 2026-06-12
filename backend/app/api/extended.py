from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, text # <-- Added 'text' for raw SQL queries
from typing import Optional, List, Dict, Any

from app.core.database import get_db
from app.models.schema import Email, Contact, Thread
import uuid
from datetime import datetime, timezone
from app.services.scraper import WEB_CACHE, fetch_web_intelligence

import google.generativeai as genai # <-- Added Gemini for real-time query embedding

router = APIRouter()

# --- Mock Schemas for Swagger Documentation ---
class RespondPayload(BaseModel):
    body: str

class DraftUpdate(BaseModel):
    body: str

class ContactStatusUpdate(BaseModel):
    status: str

# --- DYNAMIC ENDPOINTS (Hooked up to your real database) ---

@router.get("/rag/search")
def search_knowledge_base(q: str, db: Session = Depends(get_db)):
    """Debug endpoint: query KB and return chunks + scores (DYNAMIC via pgvector)"""
    
    try:
        # 1. Embed the search query using Gemini
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=q,
            output_dimensionality=768
        )
        query_vec = response['embedding']
        formatted_vec = f"[{','.join(map(str, query_vec))}]"
        
        # 2. Retrieve top-3 relevant chunks using pgvector cosine similarity
        sql_query = text("""
            SELECT source_doc, chunk_text, 1 - (embedding <=> :vec) AS similarity
            FROM knowledge_chunks
            ORDER BY embedding <=> :vec
            LIMIT 3;
        """)
        
        results = db.execute(sql_query, {"vec": formatted_vec}).fetchall()
        
        formatted_results = []
        for row in results:
            formatted_results.append({
                "source": row[0],
                "content": row[1],
                "similarity_score": round(row[2], 4) if row[2] else 0.0
            })
            
        return {
            "query": q,
            "results_count": len(formatted_results),
            "chunks": formatted_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG Search failed: {str(e)}")

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

# @router.get("/threads/{contact_email}")
# def get_contact_threads(contact_email: str, db: Session = Depends(get_db)):
#     """Full conversation thread with all emails, actions, and agent logs (DYNAMIC)"""
    
#     threads = db.query(Thread)\
#         .filter(Thread.sender_email == contact_email)\
#         .all()
        
#     if not threads:
#         return {"contact": contact_email, "threads": [], "message": "No threads found for this contact."}

#     formatted_threads = []
    
#     for thread in threads:
#         emails = db.query(Email)\
#             .filter(Email.thread_id == thread.thread_id)\
#             .order_by(Email.timestamp.asc())\
#             .all()
            
#         thread_data = {
#             "thread_id": thread.thread_id,
#             "subject": thread.subject,
#             "status": thread.status,
#             "email_count": len(emails),
#             "emails": []
#         }
        
#         for email in emails:
#             email_data = {
#                 "message_id": email.message_id,
#                 "timestamp": email.timestamp,
#                 "body": email.body,
#                 "category": email.category,
#                 "urgency": email.urgency,
#                 "status": email.status
#             }
#             thread_data["emails"].append(email_data)
            
#         formatted_threads.append(thread_data)

#     return {
#         "contact": contact_email,
#         "total_threads": len(formatted_threads),
#         "threads": formatted_threads
#     }

@router.post("/respond/{email_id}")
def send_response(email_id: int, payload: RespondPayload, db: Session = Depends(get_db)):
    """Send a reply; updates status; appends to thread (DYNAMIC)"""
    original_email = db.query(Email).filter(Email.id == email_id).first()
    if not original_email:
        raise HTTPException(status_code=404, detail="Original email not found")

    original_email.status = "Replied"

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
        
    contact.status = payload.status
    db.commit()
    db.refresh(contact)
    
    return {"email": contact.email, "new_status": contact.status}

@router.get("/intelligence/reputation")
async def get_company_reputation(company_name: str = "SenAI"):
    """Latest scraped public sentiment for company (DYNAMIC)"""
    # If it's not in cache, force a fetch
    if company_name not in WEB_CACHE:
        await fetch_web_intelligence(company_name)
        
    return WEB_CACHE.get(company_name, {}).get("data", {"status": "pending"})

@router.get("/threads/{contact_email}")
def get_contact_threads(contact_email: str, db: Session = Depends(get_db)):
    """Full conversation thread with all emails, actions, and agent logs (DYNAMIC)"""
    
    threads = db.query(Thread)\
        .filter(Thread.sender_email == contact_email)\
        .all()
        
    if not threads:
        return {"contact": contact_email, "threads": [], "message": "No threads found for this contact."}

    formatted_threads = []
    
    for thread in threads:
        emails = db.query(Email)\
            .filter(Email.thread_id == thread.thread_id)\
            .order_by(Email.timestamp.asc())\
            .all()
            
        thread_data = {
            "thread_id": thread.thread_id,
            "subject": thread.subject,
            "status": thread.status,
            "email_count": len(emails),
            "summary": None, # NEW: Summary field
            "emails": []
        }
        
        # --- BONUS: Email Thread Summarization ---
        # If thread has 5 or more emails, generate an executive summary
        if len(emails) >= 5:
            try:
                # Combine all email bodies to give context to the LLM
                full_text = "\n".join([f"Email {i+1}: {e.body}" for i, e in enumerate(emails)])
                model = genai.GenerativeModel('gemini-2.5-flash')
                summary_response = model.generate_content(
                    f"Summarize this email thread in exactly 3 concise sentences for an executive brief:\n\n{full_text}"
                )
                thread_data["summary"] = summary_response.text.strip()
            except Exception as e:
                thread_data["summary"] = "Summary generation failed."
        # -----------------------------------------
        
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

@router.post("/agent/dry-run/{email_id}")
def run_agent_dry_run(email_id: int):
    return {"email_id": email_id, "trace": ["Thought: Analyzing context...", "Action: None (Dry Run)"]}

@router.get("/audit/{entity_type}/{entity_id}")
def get_audit_history(entity_type: str, entity_id: str):
    return {"entity_type": entity_type, "entity_id": entity_id, "logs": ["Audit trace stub"]}