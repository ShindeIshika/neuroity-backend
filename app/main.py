# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import search

app = FastAPI(
    title="Neuroity Backend API",
    description="Unified dataset search API for 10+ platforms",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api/v1", tags=["search"])

@app.get("/")
def root():
    return {"message": "Neuroity Backend API is running!"}

@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}