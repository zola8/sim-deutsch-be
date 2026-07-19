import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .logging_config import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    print("Application startup complete.")
    setup_logging()
    logger.info(f"Starting {app.title} v{app.version}")
    logger.debug("Debug mode is enabled")

    # TODO await database.connect()
    # TODO setup_di_container()

    yield

    # --- SHUTDOWN ---
    # TODO await database.disconnect()
    print("Application shutting down.")
