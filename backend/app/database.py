# ============================================================================
# Database Configuration Module
# ============================================================================
# This module handles all database initialization and connection management.
# It follows the Dependency Injection principle by providing a centralized place
# for database configuration that can be easily swapped or tested.
# ============================================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# Load database credentials from environment variables with sensible defaults
# This makes the app flexible - works locally and in Docker without code changes
DB_USER = os.getenv("MYSQL_USER", "todo")
DB_PASS = os.getenv("MYSQL_PASSWORD", "todo")
DB_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")  # Default: localhost for local dev
DB_NAME = os.getenv("MYSQL_DATABASE", "todo_db")
DB_PORT = os.getenv("MYSQL_PORT", "3306")

# Build the database connection URL
# We use PyMySQL driver (pure Python) to avoid C extension compilation issues in Docker
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

print(
    "DATABASE_URL =", DATABASE_URL
)  # Log the URL for debugging (never commit sensitive data!)

# Initialize the database engine with connection pooling
# pool_pre_ping=True ensures we detect stale connections before using them
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create a session factory that we'll use to get DB sessions throughout the app
# autocommit=False means we control when transactions are committed (better for data integrity)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for all our ORM models to inherit from
Base = declarative_base()
