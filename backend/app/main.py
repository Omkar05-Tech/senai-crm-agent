from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.api import ingest, debug, rag, dashboard, extended # <-- Import your new debug file here
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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

# --- COMPONENT 7: CONSISTENT ERROR ENVELOPES ---

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Formats standard HTTP errors into the SenAI required envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.status_code,
            "message": "HTTP Error",
            "details": str(exc.detail)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Formats Pydantic validation errors into the SenAI required envelope."""
    return JSONResponse(
        status_code=422,
        content={
            "error_code": 422,
            "message": "Unprocessable Entity - Schema Validation Failed",
            "details": exc.errors()
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches any unhandled server errors (500)."""
    return JSONResponse(
        status_code=500,
        content={
            "error_code": 500,
            "message": "Internal Server Error",
            "details": str(exc)
        }
    )

# Route paths registration
app.include_router(ingest.router, prefix="/api", tags=["Ingestion Service Pipeline"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG Knowledge Pipeline"]) # <-- Register the endpoint
app.include_router(debug.router, prefix="/api", tags=["Development Utilities"]) # <-- Register the debug paths
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Frontend Dashboard Data"]) # <-- Register the dashboard paths
app.include_router(extended.router, prefix="/api", tags=["Extended Functionality"]) # <-- Register the extended paths
@app.get("/health")
def system_health_status():
    return {"status": "operational"}