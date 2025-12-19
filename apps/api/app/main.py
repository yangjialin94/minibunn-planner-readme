from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import ENV, WEB_URL
from app.core.database import Base
from app.routes import backlogs, notes, stripe, tasks, users
from app.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models to register them with Base
    from app.models import backlog, note, task, user

    # Initialize the scheduler
    start_scheduler()

    yield  # App startup complete


# Attach lifespan here
app = FastAPI(lifespan=lifespan)

# Add CORS middleware
allowed_origins = []
if WEB_URL and WEB_URL != "*":
    allowed_origins.append(WEB_URL)
    # Also add localhost and 127.0.0.1 variants for development
    if "localhost" in WEB_URL:
        allowed_origins.append(WEB_URL.replace("localhost", "127.0.0.1"))
    elif "127.0.0.1" in WEB_URL:
        allowed_origins.append(WEB_URL.replace("127.0.0.1", "localhost"))
else:
    allowed_origins = ["*"]

print("CORS will allow:", allowed_origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(backlogs.router, prefix="/backlogs", tags=["backlogs"])
app.include_router(stripe.router, prefix="/api/stripe", tags=["stripe"])
