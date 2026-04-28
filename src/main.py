import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import auth_router
from routers.users import users_router
from routers.curve_sets import curve_sets_router
from routers.analysis import analysis_router

app = FastAPI(
    title="Phasor Analyzer API",
    description="Multi-user phasor analysis backend.",
    version="2.0.0",
)

# CORS — restrict origins in production via the CORS_ORIGINS env variable
_raw_origins = os.getenv("CORS_ORIGINS", "")
allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(users_router, prefix="/users")
app.include_router(curve_sets_router, prefix="/curve-sets")
app.include_router(analysis_router, prefix="/analysis")