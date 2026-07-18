import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from api_users import users_router, user_not_found_handler, user_exists_handler
from iam import UserAlreadyExistsError, UserNotFoundError

# --- ENVIRONMENTS ---

load_dotenv()

# --- FASTAPI API ROUTERS / EXCEPTION HANDLERS ---
app: FastAPI = FastAPI()

app.include_router(users_router)

app.add_exception_handler(UserNotFoundError, user_not_found_handler)
app.add_exception_handler(UserAlreadyExistsError, user_exists_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# --- ROUTES ---

@app.get("/")
def home_page():
    return {"status": "OK"}


if __name__ == '__main__':
    print('http://localhost:8080')
    uvicorn.run(app, host="0.0.0.0", port=8080, forwarded_allow_ips="*")
