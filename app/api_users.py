from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.services import get_user_service
from iam import (
    UserService, UserCreateRequest, UserCreateResponse, UserProfile, UserUpdateRequest,
    UserNotFoundError, UserAlreadyExistsError
)

users_router = APIRouter(prefix="/api/users", tags=["users"])


# --- IAM ENDPOINTS ---

@users_router.get("/", response_model=list[UserProfile])
def list_users(user_service: UserService = Depends(get_user_service)) -> list[UserProfile]:
    """ Retrieves a list of all users. """

    return user_service.get_all_users()


@users_router.post("/", response_model=UserCreateResponse, status_code=201)
def create_user(user: UserCreateRequest,
                user_service: UserService = Depends(get_user_service)) -> UserCreateResponse:
    """ Creates a new user and returns with ID, status. """

    return user_service.create_user(user)


@users_router.get("/{user_id}", response_model=UserProfile)
def get_user(user_id: str,
             user_service: UserService = Depends(get_user_service)) -> UserProfile:
    """ Retrieves a full user profile by ID. """

    user = user_service.get_user(user_id)
    if user is None:
        raise UserNotFoundError()
    return user


@users_router.delete("/{user_id}", status_code=204)
def delete_user(user_id: str,
                user_service: UserService = Depends(get_user_service)):
    """ Deletes a user by ID. """

    user_service.delete_user(user_id)


@users_router.patch("/{user_id}", response_model=UserProfile)
def update_user(user_id: str,
                user_update: UserUpdateRequest,
                user_service: UserService = Depends(get_user_service)) -> UserProfile:
    """ Updates an existing user's username and status. """

    return user_service.update_user(user_id, user_update)


# --- CUSTOM EXCEPTION HANDLERS ---

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
