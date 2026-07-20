import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.iam.exceptions import UserNotFoundError, UserAlreadyExistsError, AuthenticationError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        logger.warning(f"User not found: {exc.user_id}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "success": False,
                "error_code": "USER_NOT_FOUND",
                "message": exc.message,
                "details": {"user_id": exc.user_id} if exc.user_id else None
            }
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
        logger.warning(f"User already exists: {exc.field}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "success": False,
                "error_code": "USER_ALREADY_EXISTS",
                "message": exc.message,
                "details": {"field": exc.field}
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # Pydantic validation errors
        details = [
            {"field": ".".join(str(loc) for loc in err["loc"] if loc != "body"), "message": err["msg"]}
            for err in exc.errors()
        ]
        logger.warning(f"Validation error on {request.url.path}: {details}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": "Invalid request payload.",
                "details": details
            }
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_error_handler(request: Request, exc: AuthenticationError):
        logger.warning(f"Authentication failed: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "error_code": "AUTHENTICATION_FAILED",
                "message": exc.message,
                "details": None
            }
        )

    # --- Global Fallback Handler ---
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception on {request.url.path}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later.",
                "details": None
            }
        )
