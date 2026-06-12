from sqlalchemy.orm import Session
from sqlalchemy import text
import google.generativeai as genai
from app.models.schema import Email
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def search_knowledge_base(query: str, db: Session) -> str:
    """Tool 1: Searches the Supabase pgvector database for company rules."""
    try:
        embedding_result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query,
            output_dimensionality=768
        )
        query_str = f"[{','.join(map(str, embedding_result['embedding']))}]"
        
        sql_query = text("""
            SELECT chunk_text FROM knowledge_chunks 
            ORDER BY embedding <=> CAST(:query_embedding AS vector) 
            LIMIT 1;
        """)
        result = db.execute(sql_query, {"query_embedding": query_str}).fetchone()
        return result[0] if result else "No relevant policy found."
    except Exception as e:
        return f"Error searching knowledge base: {str(e)}"

def get_thread_history(thread_id: str, db: Session) -> str:
    """Tool 2: Fetches previous emails from this conversation so the AI has context."""
    emails = db.query(Email).filter(Email.thread_id == thread_id).order_by(Email.timestamp.asc()).all()
    if not emails:
        return "No previous history found."
    
    history = []
    for e in emails:
        history.append(f"[{e.timestamp}] From: {e.sender} | Body: {e.body}")
    
    return "\n".join(history)

def escalate_to_human(reason: str) -> str:
    """Tool 3: Immediately stops the AI and flags the ticket for a human."""
    return f"ACTION SUCCESS: Escalated to human queue. Reason: {reason}"

def draft_reply(content: str) -> str:
    """Tool 4: Drafts the final email to send to the customer."""
    return f"ACTION SUCCESS: Drafted reply: {content}"

# --- NEW REQUIRED TOOLS FOR BOB JONES TEST CASE ---

def check_account_status(email: str) -> str:
    """Tool 5: Mocks a CRM lookup to check billing status and tier."""
    if "enterprise" in email.lower() or "bob" in email.lower():
        return f"Account {email} is on Enterprise tier. Renewal is currently ON HOLD due to billing dispute."
    return f"Account {email} is Active on Standard tier."

def flag_for_legal(issue_type: str) -> str:
    """Tool 6: Routes legal threats to the legal team."""
    return f"ACTION SUCCESS: Legal team notified. Context: {issue_type}"

def send_auto_reply(draft_id: str) -> str:
    """Tool 7: Sends an approved draft."""
    return f"ACTION SUCCESS: Auto-reply sent."

def create_internal_ticket(title: str, body: str, assignee: str) -> str:
    """Creates a support/engineering/compliance ticket."""
    return f"ACTION SUCCESS: Ticket '{title}' created and assigned to {assignee}."