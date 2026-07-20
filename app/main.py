import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.lifespan import lifespan
from app.iam.router import router as iam_router


# --- APP FACTORY ---
def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Backend API for Sim-Deutsch application",
        lifespan=lifespan,
    )

    # --- MIDDLEWARE ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- ROUTERS ---
    app.include_router(iam_router, prefix="/api/v1")

    # --- EXCEPTION HANDLERS ---
    register_exception_handlers(app)

    return app


# Create the app instance
app = create_app()


@app.get("/")
def index_page():
    return {
        "APP_NAME": settings.APP_NAME,
        "APP_VERSION": settings.APP_VERSION,
        "STATUS": "OK",
    }


# --- ENTRY POINT ---
if __name__ == '__main__':
    print(f"Starting server on http://localhost:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
