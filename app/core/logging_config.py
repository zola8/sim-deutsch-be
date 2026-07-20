import logging
import logging.config

from app.core.config import settings


def setup_logging():
    dev_formatter = {
        "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S"
    }

    prod_formatter = {
        "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s"
    }

    active_formatter = "dev" if settings.LOG_FORMAT == "dev" else "prod"

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,  # Keep default loggers (like uvicorn) alive
        "formatters": {
            "dev": dev_formatter,
            "prod": prod_formatter,
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": active_formatter,
                "stream": "ext://sys.stdout",
            },
            # You can easily add a "file" handler here later if needed
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
        },
        "loggers": {
            "uvicorn.access": {
                "level": "WARNING",  # Hide successful HTTP request spam in dev, change to INFO if needed
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # Hide SQL query spam unless LOG_LEVEL is DEBUG
                "handlers": ["console"],
                "propagate": False,
            }
        }
    }

    logging.config.dictConfig(logging_config)
