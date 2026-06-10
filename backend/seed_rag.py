import os
import google.generativeai as genai
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# This allows us to import our database schema from the app folder
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.models.schema import KnowledgeChunk

load_dotenv()

# Load credentials
DATABASE_URL = os.getenv("DATABASE_URL")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# These are the simulated company policies the PDF asked us to build
POLICIES = {
    "pricing_policy.md": (
        "Pricing & Discounts Policy: Enterprise plan costs $5,000/month billed annually. "
        "We offer a 20% discount exclusively for registered 501(c)(3) non-profit organizations. "
        "Academic and educational institutions qualify for a 15% discount for classroom use."
    ),
    "sla_policy.md": (
        "SLA Policy: Premium Enterprise contracts guarantee a 99.9% uptime. "
        "If system availability falls below 99.9% in a billing cycle, customers are eligible for a 10% credit. "
        "If system availability falls below 99.0%, a 25% bill credit is automatically issued upon human validation."
    ),
    "refund_policy.md": (
        "Refund Policy: Customers can request a full refund within 14 days of original purchase. "
        "Requests made between 15 and 30 days are eligible for a 50% pro-rata credit or refund depending on contract type. "
        "No refunds are issued after 30 days under standard circumstances."
    ),
    "compliance_faq.md": (
        "Compliance FAQ: Our infrastructure is fully HIPAA compliant and SOC2 certified. "
        "GDPR Data Portability Request Handling: Under Article 20, individuals have the right to receive their personal data. "
        "When a GDPR request is made, legal must acknowledge within 30 days. Do not send generic auto-replies."
    ),
    "escalation_matrix.md": (
        "Escalation Matrix: Security threats, active ransomware notifications, and data breaches must never receive "
        "automated AI email responses. Lock down the ticket, flag as Critical, and instantly escalate to the Security Response Unit."
    )
}

def seed_vectors():
    # Connect to Supabase
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Generating Gemini embeddings and seeding Supabase vector database...")
    
    # Loop through each policy document
    for filename, text in POLICIES.items():
        # Call Google's embedding model to turn the text into 768 numbers
        embedding_result = genai.embed_content(
            model="models/text-embedding-004",
            content=text
        )
        embedding = embedding_result['embedding']

        # Save the text and the vector to the database
        chunk = KnowledgeChunk(
            source_doc=filename,
            chunk_text=text,
            embedding=embedding
        )
        session.add(chunk)
    
    # Commit changes
    session.commit()
    session.close()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_vectors()