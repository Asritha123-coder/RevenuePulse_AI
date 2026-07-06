"""
main.py
-------
Entry point for the FastAPI application of the RevenuePulse AI Platform.
Initializes application instance and sets up routing/endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.etl import router as etl_router
from app.api.analytics import router as analytics_router
from app.api.ml import router as ml_router
from app.database.connection import test_connection

# Create FastAPI app with metadata resembling an enterprise SaaS B2B analytics platform
app = FastAPI(
    title="RevenuePulse AI - Enterprise Revenue Intelligence Platform",
    description=(
        "API service powering the RevenuePulse AI platform. "
        "Responsible for data ingestion, cleaning, validation, database pipelines, "
        "and analytic insights generation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Set up CORS middleware for integration with the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(etl_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(ml_router, prefix="/api")


@app.get("/")
def read_root():
    """Service health status check endpoint."""
    db_ok = test_connection()
    return {
        "platform": "RevenuePulse AI Enterprise Revenue Intelligence Platform",
        "api_status": "ONLINE",
        "database_connected": db_ok,
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    # Standalone execution
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
