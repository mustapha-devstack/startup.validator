from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from core.config import (
    FRONTEND_URL,
    PRODUCTION_FRONTEND_URL,
)

app = FastAPI(
    title="PlanGraph Validator API",
    version="1.0.0",
)

allowed_origins = [
    FRONTEND_URL,
    PRODUCTION_FRONTEND_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)