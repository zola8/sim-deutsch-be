from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.iam.exceptions import UserNotFoundError, UserAlreadyExistsError


def register_exception_handlers(app: FastAPI):

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        return JSONResponse(status_code=404, content={"error": str(exc)})

    @app.exception_handler(UserAlreadyExistsError)
    async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
        return JSONResponse(status_code=409, content={"error": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = [{"field": ".".join(str(loc) for loc in err["loc"]), "message": err["msg"]} for err in exc.errors()]
        return JSONResponse(
            status_code=400,
            content={"success": False, "error_code": "VALIDATION_ERROR", "message": "Invalid payload",
                     "details": details}
        )
