# ============================================================================
# Unit Tests for Task API
# ============================================================================
# These tests follow the AAA pattern (Arrange-Act-Assert) and demonstrate:
#
# CLEAN CODE PRINCIPLES:
# - Descriptive test names that explain WHAT is being tested
# - One assertion per concept (although grouped logically)
# - Setup/teardown properly isolated
#
# SOLID PRINCIPLES:
# - Dependency Injection: We override get_db with a test database
# - Interface Segregation: Tests only know about the API contract (responses)
# - Single Responsibility: Each test tests one thing
# ============================================================================

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models


# ============================================================================
# Test Database Setup
# ============================================================================
# Use an in-memory SQLite database for fast, isolated tests.
# This means each test run gets a fresh database - no side effects between tests.

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create an engine for the test database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a session factory for the test database
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database before running tests
Base.metadata.create_all(bind=engine)


# ============================================================================
# Dependency Injection Override
# ============================================================================
# This is a key pattern for testable code:
# Instead of using the real database in tests, we inject the test database.
# The app doesn't change - we just swap out the dependency.


def override_get_db():
    """Provide a test database session instead of the real one.

    This function has the same signature as the real get_db(), so FastAPI
    will use it transparently whenever a test makes a request.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Tell FastAPI: "Whenever you need get_db, use our override function instead"
app.dependency_overrides[get_db] = override_get_db

# Create a test client that can make requests without a running server
client = TestClient(app)


# ============================================================================
# Test Cases
# ============================================================================
# Each test is isolated and tests ONE behavior


def test_create_and_get_tasks():
    """Test that we can create a task and retrieve it.

    Arrange: None (starting fresh)
    Act: Create a task, then get all tasks
    Assert: Task exists with correct data
    """
    # ARRANGE & ACT: Create a new task
    r = client.post("/tasks", json={"title": "Task 1", "description": "desc"})

    # ASSERT: Creation was successful
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "Task 1"

    # ACT: Retrieve all tasks
    r = client.get("/tasks")

    # ASSERT: We got a list back
    assert r.status_code == 200
    tasks = r.json()
    assert isinstance(tasks, list)

    # ASSERT: Our created task is in the list
    assert tasks[0]["title"] == "Task 1"


def test_mark_task_complete():
    """Test that we can mark a task as completed.

    Arrange: Create a task
    Act: Mark it as complete
    Assert: Task no longer appears in the incomplete list
    """
    # ARRANGE: Create a task to complete
    r = client.post("/tasks", json={"title": "ToComplete", "description": ""})

    # Extract the task ID from the response
    task_id = r.json()["id"]

    # ACT: Mark it as complete
    r = client.patch(f"/tasks/{task_id}/complete")

    # ASSERT: Request succeeded
    assert r.status_code == 200

    # ACT: Get all incomplete tasks
    r = client.get("/tasks")

    # ASSERT: The completed task is no longer in the list
    incomplete_task_ids = [t["id"] for t in r.json()]

    # The task we just completed should not be in the list of incomplete tasks
    assert task_id not in incomplete_task_ids


def test_get_nonexistent_task():
    """Test that requesting a nonexistent task returns 404.

    Arrange: Use an ID that doesn't exist
    Act: Try to complete it
    Assert: Get a 404 error
    """
    # ARRANGE & ACT: Try to complete a task that doesn't exist
    r = client.patch("/tasks/999999/complete")

    # ASSERT: We get a proper 404 error
    assert r.status_code == 404
    assert "Task not found" in r.json()["detail"]


def test_health_check():
    """Test that the health check endpoint works.

    This is a simple endpoint used by monitoring systems.
    """
    # ACT: Call the health endpoint
    r = client.get("/api/health")

    # ASSERT: It returns 200 and says everything is ok
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
