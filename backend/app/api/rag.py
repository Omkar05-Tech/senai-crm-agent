from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import google.generativeai as genai
import os
from app.core.database import get_db
from app.models.schema import KnowledgeChunk

router = APIRouter()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Pydantic Schemas for Validation
class RagSearchRequest(BaseModel):
    query: str

class PolicyUploadRequest(BaseModel):
    title: str
    content: str

@router.post("/search", status_code=status.HTTP_200_OK)
def debug_rag_search(payload: RagSearchRequest, db: Session = Depends(get_db)):
    """
    RAG Search Debugging Endpoint: Tests the vector distance matching.
    Takes a query string and returns the closest matching company policy.
    """
    try:
        # Embed the query
        embedding_result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=payload.query
        )
        query_vec = embedding_result['embedding']
        query_str = f"[{','.join(map(str, query_vec))}]"
        
        # Execute Vector Math
        sql_query = text("""
            SELECT source_doc, chunk_text FROM knowledge_chunks 
            ORDER BY embedding <=> CAST(:query_embedding AS vector) 
            LIMIT 1;
        """)
        
        result = db.execute(sql_query, {"query_embedding": query_str}).fetchone()
        
        if result:
            return {
                "status": "success",
                "matched_document": result[0],
                "retrieved_policy": result[1]
            }
        return {"status": "not_found", "detail": "No policies found in database."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vector search failed: {str(e)}")


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_new_policy(payload: PolicyUploadRequest, db: Session = Depends(get_db)):
    """
    Allows dynamic ingestion of new corporate policies via the API.
    """
    try:
        # Generate the embedding for the new rule
        embedding_result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=payload.content
        )
        
        # Save to database
        chunk = KnowledgeChunk(
            source_doc=f"{payload.title}.md",
            chunk_text=payload.content,
            embedding=embedding_result['embedding']
        )
        db.add(chunk)
        db.commit()
        
        return {"status": "success", "detail": f"Policy '{payload.title}' embedded and saved."}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))