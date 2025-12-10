# ============================================================================
# Main API Application (Entry Point)
# ============================================================================
# This is the FastAPI application that handles all HTTP requests.
#
# CLEAN CODE PRINCIPLES APPLIED:
# - Clear, descriptive names for functions and variables
# - Each function does ONE thing (Single Responsibility)
# - Comments explain WHY, not WHAT (the code shows WHAT it does)
# - Proper error handling and logging
#
# SOLID PRINCIPLES APPLIED:
# - Dependency Injection (get_db): Makes testing easy, decouples code
# - Single Responsibility: Controllers delegate to CRUD layer
# - Open/Closed: New endpoints can be added without modifying existing ones
# - Interface Segregation: Schemas define clear contracts
# - Dependency Inversion: Depends on abstractions (Session), not concrete DB
# ============================================================================

import time
import logging
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from . import models, schemas, crud
from .database import engine, SessionLocal, Base


# Configure logging to see what's happening at runtime
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the FastAPI application
app = FastAPI(title="Todo Assessment API")


# ============================================================================
# SECTION 1: Static File Serving (Frontend)
# ============================================================================
# Serve the frontend files alongside the API. This keeps everything in
# one container but separates concerns (frontend in /frontend folder).

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

if FRONTEND_DIR.exists():
    logger.info(f"Serving frontend from: {FRONTEND_DIR}")

    # Mount static files (CSS, JS) at /static
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Serve the main HTML page at the root path
    @app.get("/")
    def serve_frontend():
        """Return the main frontend HTML page."""
        return FileResponse(FRONTEND_DIR / "index.html")

else:
    logger.warning(f"Frontend not found at: {FRONTEND_DIR}")


# ============================================================================
# SECTION 2: CORS Configuration
# ============================================================================
# Allow cross-origin requests so the frontend can call the API.
# In production, you'd restrict this to specific origins instead of "*".

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: In production, set this to actual domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# SECTION 3: Dependency Injection (Database Session)
# ============================================================================
# This follows the Dependency Injection principle - the app doesn't create
# sessions directly; it asks for them via the 'Depends' system.
# This makes it easy to mock the database in tests.


def get_db():
    """Provide a database session to route handlers.

    This is a generator that yields a session and ensures it's closed
    even if an error occurs. FastAPI handles the yield automatically.

    Usage in handlers: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Always close the connection, whether successful or not
        db.close()


# ============================================================================
# SECTION 4: Application Startup
# ============================================================================
# When the API starts, we wait for the database to be ready and create tables.
# This is important in Docker where MySQL might not be ready immediately.


@app.on_event("startup")
def on_startup():
    """Initialize the application on startup.

    - Wait up to 15 seconds for the database to become available
    - Create all tables defined in our ORM models
    """
    # Try to connect to the database, with retry logic
    for attempt in range(15):
        try:
            conn = engine.connect()
            conn.close()
            logger.info("✓ Database connection successful")
            break
        except OperationalError:
            # Database not ready yet, wait and retry
            if attempt < 14:  # Don't sleep on the last attempt
                logger.info(
                    f"Database not ready, retrying... (attempt {attempt + 1}/15)"
                )
                time.sleep(1)

    # Create all database tables (if they don't exist)
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created")


# ============================================================================
# SECTION 5: API Routes
# ============================================================================
# RESTful endpoints for task management.
# Each endpoint follows the Single Responsibility Principle:
# - It validates input (done by Pydantic schemas)
# - It delegates business logic to the CRUD layer
# - It formats the response


@app.post("/tasks", response_model=schemas.TaskRead)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """Create a new task.

    The client sends a title and optional description.
    The API generates the ID and timestamp.

    Args:
        task: TaskCreate schema with title and optional description
        db: Database session (injected by FastAPI)

    Returns:
        The created Task with its ID and timestamp
    """
    return crud.create_task(db, task)


@app.get("/tasks", response_model=list[schemas.TaskRead])
def list_tasks(limit: int = 5, db: Session = Depends(get_db)):
    """Get recent incomplete tasks.

    Returns the newest incomplete tasks, limited to avoid overwhelming
    the frontend with too much data.

    Args:
        limit: Maximum tasks to return (default: 5, query param: ?limit=10)
        db: Database session (injected by FastAPI)

    Returns:
        List of Task objects sorted by newest first
    """
    return crud.get_recent_tasks(db, limit)


@app.patch("/tasks/{task_id}/complete", response_model=schemas.TaskRead)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Mark a task as complete.

    Updates the task's completed status to true. If the task ID doesn't
    exist, returns a 404 error.

    Args:
        task_id: The ID of the task to complete (from URL path)
        db: Database session (injected by FastAPI)

    Returns:
        The updated Task object

    Raises:
        HTTPException: 404 if task is not found
    """
    task = crud.mark_task_completed(db, task_id)

    if not task:
        # Task doesn't exist - return a proper HTTP error
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.get("/api/health")
def health_check():
    """Health check endpoint for monitoring.

    Returns a simple status to confirm the API is running and responsive.
    This is typically used by load balancers, Docker, or monitoring systems
    to ensure the application is healthy.

    Returns:
        dict with status "ok"
    """
    return {"status": "ok"}
