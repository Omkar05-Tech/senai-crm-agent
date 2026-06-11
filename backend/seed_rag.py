import os
import google.generativeai as genai
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

POLICIES = {
    "pricing_policy.md": "Pricing Policy: We offer a 20% discount exclusively for registered 501(c)(3) non-profit organizations.",
    "sla_policy.md": "SLA Policy: If system availability falls below 99.0%, a 25% bill credit is issued.",
    "escalation_matrix.md": "Escalation Matrix: Security threats and active ransomware must never receive automated replies. Escalate to Security."
}

def force_seed_database():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("--- STARTING DIAGNOSTIC SEEDER ---")

    try:
        # 1. Force drop and recreate the table with 3072 dimensions
        print("1. Resetting database table...")
        session.execute(text("DROP TABLE IF EXISTS knowledge_chunks;"))
        session.execute(text("""
            CREATE TABLE knowledge_chunks (
                id SERIAL PRIMARY KEY,
                source_doc VARCHAR,
                chunk_text TEXT,
                embedding vector(3072),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        session.commit()
        print("   -> Table created successfully with 3072 dimensions.")

        # 2. Test the Embedding generation using the stable 001 model
        print("\n2. Generating embeddings from Gemini...")
        for filename, doc_text in POLICIES.items():
            try:
                response = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=doc_text
                )
                vec = response['embedding']
                print(f"   -> [SUCCESS] Generated vector for {filename} (Size: {len(vec)} dimensions)")
                
                if len(vec) != 3072:
                    print(f"   -> [FATAL ERROR] Expected 3072 dimensions, but got {len(vec)}.")
                    return

                # 3. Save to database using raw SQL
                session.execute(
                    text("INSERT INTO knowledge_chunks (source_doc, chunk_text, embedding) VALUES (:doc, :txt, :emb)"),
                    {"doc": filename, "txt": doc_text, "emb": f"[{','.join(map(str, vec))}]"}
                )
                session.commit()
                print(f"   -> [SAVED] {filename} securely stored in Supabase.")

            except Exception as inner_e:
                print(f"   -> [API/DB ERROR] Failed on {filename}: {str(inner_e)}")
                session.rollback()

    except Exception as e:
        print(f"\n[CRITICAL FAILURE] {str(e)}")
    finally:
        session.close()
        print("\n--- SEEDING PROCESS COMPLETE ---")

if __name__ == "__main__":
    force_seed_database()