from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.database import db_manager

app = FastAPI(
    title="Blog Backend API",
    description="Backend service for blog application",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    pass

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "Blog Backend API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}