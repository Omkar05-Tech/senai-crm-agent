from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import ingest, debug, rag, dashboard # <-- Import your new debug file here

# Automatically creates matching schema layouts inside Supabase database instance on container boot
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic CRM Intelligence Engine API Platform", 
    version="1.0.0"
)

# 2. Add the CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this would be your exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route paths registration
app.include_router(ingest.router, prefix="/api", tags=["Ingestion Service Pipeline"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG Knowledge Pipeline"]) # <-- Register the endpoint
app.include_router(debug.router, prefix="/api", tags=["Development Utilities"]) # <-- Register the debug paths
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Frontend Dashboard Data"]) # <-- Register the dashboard paths

@app.get("/health")
def system_health_status():
    return {"status": "operational"}