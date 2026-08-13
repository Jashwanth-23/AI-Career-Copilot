"""
main.py - FastAPI Application Entry Point

Responsibilities:
- Initializes FastAPI application instance
- Registers middleware (CORS, Logging, Exception Handlers)
- Mounts API routers from app.api package
- Defines root/health check endpoints
"""
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from app.api.ats import router as ats_router
from app.api.auth import router as auth_router
from app.api.job_recommendation import router as job_recommendation_router
from app.api.learning_roadmap import router as learning_roadmap_router
from app.api.mock_interview import router as mock_interview_router
from app.api.parser import router as parser_router
from app.api.resume import router as resume_router
from app.api.resume_analysis import router as resume_analysis_router
from app.api.skill_gap import router as skill_gap_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI Career Copilot SaaS application",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origin.strip() for origin in origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers under /api/v1 prefix
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(resume_router, prefix=settings.API_V1_STR)
app.include_router(parser_router, prefix=settings.API_V1_STR)
app.include_router(resume_analysis_router, prefix=settings.API_V1_STR)
app.include_router(ats_router, prefix=settings.API_V1_STR)
app.include_router(skill_gap_router, prefix=settings.API_V1_STR)
app.include_router(learning_roadmap_router, prefix=settings.API_V1_STR)
app.include_router(job_recommendation_router, prefix=settings.API_V1_STR)
app.include_router(mock_interview_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "status": "success",
        "message": "AI Career Copilot API is running 🚀",
        "version": "0.1.0"
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "healthy"
    }
