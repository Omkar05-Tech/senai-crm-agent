import os
import glob
import google.generativeai as genai
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# The path where we saved the 6 markdown files
DOCS_DIR = "data/knowledge_base"

def force_seed_database():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("--- STARTING ENTERPRISE RAG SEEDER ---")

    try:
        # 1. Reset the table
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

        # 2. Read and Chunk the Markdown Files
        print("\n2. Reading and Chunking Knowledge Base...")
        markdown_files = glob.glob(os.path.join(DOCS_DIR, "*.md"))
        
        if not markdown_files:
            print(f"❌ Error: No markdown files found in {DOCS_DIR}")
            return

        # REQUIREMENT: Chunk into 300-500 tokens with overlap
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400, # Approx tokens/chars depending on config
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " "]
        )

        all_chunks = []
        for file_path in markdown_files:
            filename = os.path.basename(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            chunks = text_splitter.split_text(content)
            for chunk in chunks:
                all_chunks.append({"filename": filename, "text": chunk})
                
        print(f"   -> Successfully created {len(all_chunks)} overlapping chunks.")

        # 3. Generate Embeddings and Save to Supabase
        print("\n3. Generating embeddings from Gemini...")
        for item in all_chunks:
            filename = item["filename"]
            doc_text = item["text"]
            
            try:
                response = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=doc_text,
                    output_dimensionality=768
                )
                vec = response['embedding']
                
                # Database insertion using raw SQL
                session.execute(
                    text("INSERT INTO knowledge_chunks (source_doc, chunk_text, embedding) VALUES (:doc, :txt, :emb)"),
                    {"doc": filename, "txt": doc_text, "emb": f"[{','.join(map(str, vec))}]"}
                )
                session.commit()
                print(f"   -> [SAVED] Chunk from {filename} securely stored in Supabase.")

            except Exception as inner_e:
                print(f"   -> [API/DB ERROR] Failed on chunk from {filename}: {str(inner_e)}")
                session.rollback()

    except Exception as e:
        print(f"\n[CRITICAL FAILURE] {str(e)}")
    finally:
        session.close()
        print("\n--- SEEDING PROCESS COMPLETE ---")

if __name__ == "__main__":
    force_seed_database()