import json
import google.generativeai as genai
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.schema import KnowledgeChunk
from app.core.config import settings
import os

# Initialize Gemini Client
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_rag_context(email_body: str, db: Session) -> str:
    """
    Converts the incoming email into a vector and asks PostgreSQL to find 
    the closest matching policy document using Cosine Similarity (<=>).
    """
    try:
        # Embed the incoming email text
        embedding_result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=email_body
        )
        query_embedding = embedding_result['embedding']
        
        # Format the Python list into a format PostgreSQL pgvector understands
        query_str = f"[{','.join(map(str, query_embedding))}]"
        
        # Execute the math search directly in the database
        sql_query = text("""
            SELECT chunk_text FROM knowledge_chunks 
            ORDER BY embedding <=> CAST(:query_embedding AS vector) 
            LIMIT 1;
        """)
        
        result = db.execute(sql_query, {"query_embedding": query_str}).fetchone()
        
        # Return the retrieved rulebook text
        return result[0] if result else "No explicit corporate policy guidelines found."
    except Exception:
        return "Vector engine retrieval failure."

def analyze_email_intelligence(email_body: str, subject: str, db: Session) -> dict:
    """
    Passes the email and the company policy to Gemini Flash.
    Forces the AI to output pure JSON so our code can read the classification.
    """
    # 1. Fetch the relevant company rules
    policy_context = get_rag_context(email_body, db)

    # 2. Build the strict prompt
    system_prompt = (
        "You are an elite enterprise CRM triage classifier. Your output MUST be strict JSON matching this structure exactly:\n"
        "{\n"
        "  \"sentiment_score\": -1.0 to 1.0,\n"
        "  \"category\": \"Billing\" | \"Technical Support\" | \"Legal & Compliance\" | \"General Inquiry\" | \"Spam\",\n"
        "  \"urgency\": \"Low\" | \"Medium\" | \"High\" | \"Critical\",\n"
        "  \"requires_human\": true | false,\n"
        "  \"confidence\": 0.0 to 1.0,\n"
        "  \"reasoning\": \"1 sentence justification citing internal policy rules\"\n"
        "}\n"
        f"Ground Truth Company Guidelines:\n{policy_context}"
    )

    try:
        # 3. Call Gemini Flash, enforcing application/json mode
        model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_prompt)
        response = model.generate_content(
            f"Subject: {subject}\nBody: {email_body}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.0 # Keep temperature at 0 for logical consistency
            )
        )
        
        # 4. Convert the text response back into a Python dictionary
        return json.loads(response.text)
    except Exception as e:
        # Fallback safety net if the AI crashes
        return {
            "sentiment_score": 0.0,
            "category": "General Inquiry",
            "urgency": "Medium",
            "requires_human": True,
            "confidence": 0.0,
            "reasoning": f"Intelligence parser exception: {str(e)}"
        }