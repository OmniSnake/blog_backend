from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.database import db_manager
from sqlalchemy import text

async def startup():
    """Действия при запуске приложения"""
    print("🚀 Blog Backend API starting up...")
    try:
        async with db_manager.engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("✅ Database connection established")
            else:
                print("❌ Database connection test failed")
    except Exception as e:
        print(f"❌ Database connection error: {e}")

async def shutdown():
    """Действия при остановке приложения"""
    print("🛑 Blog Backend API shutting down...")
    await db_manager.engine.dispose()
    print("✅ Database connections closed")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()

app = FastAPI(
    title="Blog Backend API",
    description="Backend service for blog application",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """Корневой endpoint"""
    return {"message": "Blog Backend API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}