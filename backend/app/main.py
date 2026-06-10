from fastapi import FastAPI
from app.core.database import engine, Base
from app.api import ingest, debug # <-- Import your new debug file here

# Automatically creates matching schema layouts inside Supabase database instance on container boot
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Agentic CRM Intelligence Engine API Platform", 
    version="1.0.0"
)

# Route paths registration
app.include_router(ingest.router, prefix="/api", tags=["Ingestion Service Pipeline"])
app.include_router(debug.router, prefix="/api", tags=["Development Utilities"]) # <-- Register the debug paths

@app.get("/health")
def system_health_status():
    return {"status": "operational"}