from fastapi import FastAPI # type: ignore # typ
from fastapi.middleware.cors import CORSMiddleware # type: ignore

from .database import Base, engine
from . import models

from .routers import auth
from .routers import clients
from .routers import services
from .routers import templates
from .routers import engagements
from .routers import tasks
from .routers import audit
from .routers import dashboard
from .routers import users

# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Task & Engagement Management Tool",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://task-engagement-management-tool.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

app.include_router(clients.router)

app.include_router(services.router)

app.include_router(templates.router)

app.include_router(engagements.router)

app.include_router(tasks.router)

app.include_router(audit.router)

app.include_router(dashboard.router)

app.include_router(users.router)


@app.get("/")
def root():
    return {
        "message": "Task & Engagement Management API is running"
    }


# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }