"""PetOrbit Backend API — FastAPI entry point"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import jobs, results

app = FastAPI(
    title="PetOrbit API",
    description="AI novel view synthesis for interactive 180° pet head orbit",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — 生產環境請改為明確 origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router)
app.include_router(results.router)


@app.get("/health", tags=["system"])
def health():
    return {
        "status": "ok",
        "service": "pet-orbit-api",
        "version": "2.0.0",
        "modes": ["static_orbit", "live_orbit"],
    }
