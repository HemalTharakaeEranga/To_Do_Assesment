# ============================================================================
# Database Models (ORM Layer)
# ============================================================================
# These models represent the actual database tables.
# They follow the "Liskov Substitution Principle" - all models inherit from Base
# and work the same way with SQLAlchemy.
# ============================================================================

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from .database import Base


class Task(Base):
    """Represents a Task entity in the database.

    This model maps to the 'task' table and contains all the data needed
    to manage a todo item (title, description, completion status, and timestamp).
    """

    __tablename__ = "task"

    # Primary key - uniquely identifies each task
    id = Column(Integer, primary_key=True, index=True)

    # Task title - required field, max 255 characters
    title = Column(String(255), nullable=False)

    # Task description - optional, can be null, max 1000 characters
    description = Column(String(1000), nullable=True)

    # Tracks whether the task is done or not
    # We index this because we often filter by completion status
    completed = Column(Boolean, default=False, nullable=False, index=True)

    # Timestamp for when the task was created
    # Database automatically sets this to the current time (server-side)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
