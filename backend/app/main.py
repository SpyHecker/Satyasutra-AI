"""
SatyaSutra Backend — FastAPI Application

Main entry point. Configures CORS, registers routes, and exposes a
health-check endpoint. Creates required directories and initializes
MongoDB connection on startup.
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.evidence import router as evidence_router
from app.routes.auth import router as auth_router
from app.routes.chatbot import router as chatbot_router
from app.db.sqlite import init_sqlite_db, get_db_path

# --- MongoDB code commented out per instruction (using SQLite for login) ---
# from app.db.mongodb import (
#     connect_to_mongodb,
#     close_mongodb_connection,
#     is_mongodb_ready,
#     get_mongodb_db_name,
# )

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Startup / Shutdown lifecycle
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create required directories and initialize database on startup."""
    dirs = [Path("uploads"), Path("data")]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured directory: {d.resolve()}")

    # Initialize SQLite database for authentication
    init_sqlite_db()
    logger.info(f"Active authentication database: SQLite ({get_db_path()})")

    # --- MongoDB connection commented out per instruction (using SQLite for login) ---
    # mongo_ok = connect_to_mongodb()
    # if mongo_ok:
    #     logger.info(f"Active database backend: MongoDB ({get_mongodb_db_name()})")
    # else:
    #     logger.info("Active database backend: Local JSON Store (ready for MongoDB connection)")

    yield

    # --- MongoDB shutdown commented out per instruction ---
    # close_mongodb_connection()
    logger.info("Shutting down SatyaSutra API")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SatyaSutra API",
    description="AI-assisted investigation tool — evidence analysis, knowledge graph, timeline, and report generation.",
    version="0.2.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# CORS — allow Vite dev server during development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(evidence_router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(chatbot_router, prefix="/api/chatbot", tags=["AI Assistant"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@app.get("/api/health", tags=["System"])
async def health_check():
    """Liveness & database readiness probe."""
    # --- MongoDB check commented out per instruction (using SQLite for login) ---
    # mongo_ready = is_mongodb_ready()
    return {
        "status": "ok",
        "service": "SatyaSutra AI Forensic API",
        "version": "0.2.0",
        "database": {
            "type": "sqlite",
            "connected": True,
            "database_file": str(get_db_path()),
        },
    }


# ---------------------------------------------------------------------------
# Dev server entry point:  python -m app.main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
