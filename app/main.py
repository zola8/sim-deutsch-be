import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from iam import UserService, UserCreateRequest, UserCreateResponse

load_dotenv()

app: FastAPI = FastAPI()
# TODO app context? + For larger apps, consider using FastAPI's `Depends` for dependency injection
user_service = UserService()


@app.get("/")
def home_page():
    return {"status": "OK"}


# --- IAM ENDPOINTS ---

@app.get("/users", response_model=list[UserCreateResponse])
def list_users():
    """Retrieves a list of all users."""
    return user_service.get_all_users()

@app.post("/users/create", response_model=UserCreateResponse, status_code=201)
def create_user(user: UserCreateRequest):
    return user_service.create_user(user)

# TODO handle http exceptions in FE
@app.get("/user/{user_id}", response_model=UserCreateResponse)
def get_user(user_id: str):
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# TODO delete - change user status



if __name__ == '__main__':
    print('http://localhost:8080')
    uvicorn.run(app, host="0.0.0.0", port=8080, forwarded_allow_ips="*")
