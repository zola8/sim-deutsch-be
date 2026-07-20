import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import setup_database
from app.core.logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print("Application startup complete.")

    setup_logging()
    setup_database()

    logger.info(f"Starting {app.title} v{app.version}")
    logger.debug("Debug mode is enabled")

    yield

    # --- SHUTDOWN ---
    print("Application shutting down.")
