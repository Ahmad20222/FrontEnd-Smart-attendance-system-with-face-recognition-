"""
Application entrypoint for the Smart Attendance System backend.

This module is responsible for:
- Creating database tables on startup.
- Initializing the global `InsightFaceEmbedder` instance used by the
  attendance router.
- Wiring FastAPI routers and CORS configuration.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.config.dbsetup import engine
from app.routers import attendance_router as attendance_module
from app.routers.admin_router import admin_router
from app.routers.attendance_router import router as attendance_router
from app.routers.person_router import person_router
from app.routers.status_router import status_router
from app.services.face_service import InsightFaceEmbedder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context.

    On startup:
    - Creates/updates database tables.
    - Initializes the global `InsightFaceEmbedder` used in the
      `attendance_router` module.

    On shutdown:
    - Logs graceful shutdown information.
    """
    logger.info("Starting application...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created/verified")
    logger.info("Initializing InsightFace embedder...")
    attendance_module.embedder = InsightFaceEmbedder()
    logger.info("InsightFace embedder initialized successfully")
    try:
        yield
    except asyncio.CancelledError:
        logger.info("Application shutdown requested")
        pass
    finally:
        logger.info("Application shutting down")
        pass


app = FastAPI(title="Smart Attendance System API", lifespan=lifespan)

#: Allowed frontend origins.
origins = [
    "http://127.0.0.1:5000",
    "http://localhost:5000",
    # Dev tunnels – update/remove as needed in your environment.
    "https://45p38rww-5000.euw.devtunnels.ms",
    "https://45p38rww-8000.euw.devtunnels.ms",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,          
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(person_router)
app.include_router(status_router)
app.include_router(admin_router)
app.include_router(attendance_router)
