from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    company = Column(String, nullable=True)
    status = Column(String, default="Active") # VIP | Blocked | Active | Churned
    account_value = Column(Float, default=0.0)
    churn_risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_contact_at = Column(DateTime(timezone=True), onupdate=func.now())

class Thread(Base):
    __tablename__ = "threads"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, unique=True, index=True, nullable=False)
    subject = Column(String, nullable=True)
    sender_email = Column(String, ForeignKey("contacts.email"))
    first_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default="Open") # Open | Resolved | Escalated | Ignored
    assigned_to = Column(String, nullable=True)
    
    emails = relationship("Email", back_populates="thread")

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    thread_id = Column(String, ForeignKey("threads.thread_id"))
    message_id = Column(String, unique=True, index=True, nullable=False)
    sender = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    body = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True))
    
    # Intelligence evaluation tracking states (Populated in Sprint 2)
    sentiment_score = Column(Float, nullable=True)
    category = Column(String, nullable=True)
    urgency = Column(String, nullable=True)
    requires_human = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)
    raw_entities = Column(JSONB, nullable=True)
    status = Column(String, default="Received") # Received | Processing | Replied | Escalated
    
    thread = relationship("Thread", back_populates="emails")

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"
    id = Column(Integer, primary_key=True, index=True)
    source_doc = Column(String, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(1536)) # Fixed vector dimensions matching standard OpenAI Ada/Text-3 layouts
    created_at = Column(DateTime(timezone=True), server_default=func.now())