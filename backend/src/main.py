"""
LinkedIn AI AutoPost - Backend Application

FastAPI application entry point with route aggregation and health check.
"""
import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.api.linkedin_router import router as linkedin_router
from src.api.post_router import router as post_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="LinkedIn AI AutoPost",
    description="AI-powered LinkedIn post generation with approval workflow",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(linkedin_router, prefix="/linkedin", tags=["LinkedIn"])
app.include_router(post_router, tags=["Posts"])


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "LinkedIn automation service is running"}


# Mount generated images directory
os.makedirs("generated_images", exist_ok=True)
try:
    app.mount("/images", StaticFiles(directory="generated_images"), name="images")
except RuntimeError:
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
