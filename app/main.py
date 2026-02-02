from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

# Import all models to ensure they are registered with SQLAlchemy
from app.models import user, course, enrollment, progress, review

# Import routers
from app.routers import auth, users, courses, enrollments, progress

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/",
    description="Online Course Enrollment System API with JWT Authentication"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(enrollments.router)
app.include_router(progress.router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy", "app": settings.app_name, "version": settings.app_version}
