"""PetOrbit Backend API — FastAPI entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import jobs, results

app = FastAPI(
    title="PetOrbit API",
    description="AI novel view synthesis pipeline for interactive 180° pet head orbit",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs.router, prefix="/api")
app.include_router(results.router, prefix="/api")

@app.get("/health")
def health():
    return {"status": "ok", "service": "pet-orbit-api"}
