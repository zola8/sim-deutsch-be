from fastapi import APIRouter, HTTPException

from app.dependencies import UserServiceDep, AuthServiceDep
from app.iam.api.schema_authentication import RegisterWithPasswordRequest, LoginWithPasswordRequest
from app.iam.api.schema_user_management import UserUpdateRequest
from app.iam.api.schema_user_profile import UserProfile

router = APIRouter()


# --- User Management Endpoints (Admin) ---

@router.get("/users/{user_id}", response_model=UserProfile)
def get_user(user_id: str, user_service: UserServiceDep):
    return user_service.get_user(user_id)


@router.get("/users", response_model=list[UserProfile])
def get_all_users(user_service: UserServiceDep):
    return user_service.get_all_users()


@router.put("/users/{user_id}", response_model=UserProfile)
def update_user(user_id: str, request: UserUpdateRequest, user_service: UserServiceDep):
    return user_service.update_user(user_id, request)


@router.delete("/users/{user_id}")
def delete_user(user_id: str, user_service: UserServiceDep):
    deleted = user_service.delete_user(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}


# --- Authentication Endpoints (User Self-Service) ---

@router.post("/auth/register")
def register(request: RegisterWithPasswordRequest, auth_service: AuthServiceDep):
    user = auth_service.register_with_password(request)
    return {
        "user_id": user.user_id,
        "status": user.status,
        "message": "Registration successful"
    }


@router.post("/auth/login")
def login(request: LoginWithPasswordRequest, auth_service: AuthServiceDep):
    user = auth_service.login_with_password(request)
    # TODO: Generate JWT token here in a later step
    return {
        "access_token": "placeholder-token",
        "token_type": "bearer",
        "user": user
    }
