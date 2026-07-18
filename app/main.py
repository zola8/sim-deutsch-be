import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from iam import (
    UserService, UserCreateRequest, UserCreateResponse, UserProfile,
    UserAlreadyExistsError, UserNotFoundError
)

load_dotenv()

# TODO app context? + For larger apps, consider using FastAPI's `Depends` for dependency injection
app: FastAPI = FastAPI()
user_service = UserService()


# --- CUSTOM EXCEPTION HANDLERS ---
# These remain the same and will automatically catch the new password/email validations

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"]) if error["loc"] else None
        details.append({"field": field, "message": error["msg"]})

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request payload.",
            "details": details
        },
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_exists_handler(request: Request, exc: UserAlreadyExistsError):
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "error_code": "USER_EXISTS",
            "message": f"Creation failed: A user with this {exc.field} already exists.",
            "details": [{"field": exc.field, "message": "Must be unique"}]
        }
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "error_code": "USER_NOT_FOUND",
            "message": "The requested user does not exist.",
            "details": []
        }
    )


# --- ROUTES ---

@app.get("/")
def home_page():
    return {"status": "OK"}


# --- IAM ENDPOINTS ---

@app.get("/users", response_model=list[UserProfile])
def list_users():
    """Retrieves a list of all users."""
    return user_service.get_all_users()


@app.post("/users", response_model=UserCreateResponse, status_code=201)
def create_user(user: UserCreateRequest):
    return user_service.create_user(user)


@app.get("/users/{user_id}", response_model=UserProfile)
def get_user(user_id: str):
    user = user_service.get_user(user_id)
    if user is None:
        raise UserNotFoundError()
    return user


@app.delete("/users/{user_id}", response_model=UserCreateResponse)
def delete_user(user_id: str):
    return user_service.delete_user(user_id)


if __name__ == '__main__':
    print('http://localhost:8080')
    uvicorn.run(app, host="0.0.0.0", port=8080, forwarded_allow_ips="*")
