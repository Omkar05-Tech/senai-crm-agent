from fastapi import FastAPI
from app.core.database import engine, Base
from app.api import ingest

# Automatically creates matching schema layouts inside Supabase database instance on container boot
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic CRM Intelligence Engine API Platform", 
    version="1.0.0"
)

app.include_router(ingest.router, prefix="/api", tags=["Ingestion Service Pipeline"])

@app.get("/health")
def system_health_status():
    return {"status": "operational"}