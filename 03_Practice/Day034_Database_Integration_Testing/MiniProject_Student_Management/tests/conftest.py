"""
conftest.py — Shared pytest fixtures for Day 033: Automated Testing.

Why conftest.py?
----------------
pytest automatically discovers and loads this file before running any test
in the same directory or any subdirectory.  Fixtures defined here are
available to ALL test modules without any import.

Fixtures defined here:
  - sample_student        : A ready-made Student_response_model for reuse.
  - mock_student_service  : A MagicMock wired as a fake StudentService.
  - api_client_with_mock  : A FastAPI TestClient with the real service replaced
                            by mock_student_service via dependency_overrides.

Integration and unit fixtures live in their own modules (closer to the tests
that need them) to keep the global fixture space small.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# Make the project root importable.
# When pytest is invoked from the project root the parent of 'tests/' is
# already on sys.path.  This guard handles the edge case where pytest is
# run from inside the tests/ directory itself.
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Now safe to import application modules
# ---------------------------------------------------------------------------
from models.student import Student_response_model


# ─────────────────────────────────────────────────────────────────────────────
# Shared data fixture
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_student() -> Student_response_model:
    """
    Return a pre-built Student_response_model that can be reused across all
    test categories without repeating constructor arguments.

    This is a plain Python object — no database is involved.
    """
    return Student_response_model(
        id=1,
        name="Alice Test",
        age=22,
        city="Mumbai",
        email="alice.test@example.com",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Mock service fixture (used by API tests via dependency_overrides)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_student_service():
    """
    Return a MagicMock that mimics StudentService.

    Used in API tests (Exercise 9) where we override the FastAPI dependency
    so the TestClient never touches a real database.

    Each test configures return_value / side_effect on the mock's methods
    to control exactly what the fake service returns.
    """
    return MagicMock()


# ─────────────────────────────────────────────────────────────────────────────
# Mock DB helper (used to prevent lifespan from connecting to Docker's DB)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db_helper():
    """
    Return a MagicMock that satisfies the DatabaseHelper interface.

    WHY IS THIS NEEDED?
    -------------------
    The FastAPI lifespan (main.py) calls db_helper.open_pool() on startup
    and db_helper.close_pool() on shutdown.  Even when the StudentService is
    overridden, the lifespan still runs — and the real DatabaseHelper would
    try to connect to 'host=db' (the Docker Compose service name), which is
    not reachable on a local machine without Docker.

    By overriding get_db_helper with this no-op mock, the lifespan completes
    instantly without any network I/O.  The API tests remain completely
    self-contained — no Docker, no PostgreSQL, no .env required.

    This is the correct clean-architecture testing pattern:
      API tests should test HTTP routing + serialisation + exception mapping.
      They should not depend on infrastructure at all.
    """
    mock = MagicMock()
    # Ensure open_pool and close_pool are no-ops (default MagicMock behaviour)
    mock.open_pool.return_value = None
    mock.close_pool.return_value = None
    return mock


# ─────────────────────────────────────────────────────────────────────────────
# API TestClient with dependency override (Exercise 8, 9, 10)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client(mock_student_service, mock_db_helper):
    """
    Return a FastAPI TestClient with the real StudentService replaced by
    mock_student_service through FastAPI's dependency_overrides mechanism.

    Why dependency_overrides?
    -------------------------
    FastAPI's Depends() system is the same "seam" that Dependency Injection
    creates for testing.  By overriding get_student_service we swap the
    entire production wiring (DatabaseHelper → Repository → Service) with a
    single mock object — without touching any production code.

    Why patch dependencies._db_helper (not override get_db_helper)?
    ----------------------------------------------------------------
    The lifespan in main.py calls get_db_helper() DIRECTLY — not via
    FastAPI's Depends() system.  That means dependency_overrides does NOT
    intercept it.

    Instead, we use unittest.mock.patch to swap the global `_db_helper`
    singleton inside the dependencies module for the duration of the test.
    The lifespan then calls open_pool()/close_pool() on our no-op mock
    instead of trying to reach Docker's 'db' host.

    The override is cleared after every test via the yield + cleanup pattern,
    ensuring tests remain isolated from one another.
    """
    from unittest.mock import patch
    from main import app
    from dependencies import get_student_service

    # Override 1: Replace the real service with our mock via DI system.
    app.dependency_overrides[get_student_service] = lambda: mock_student_service

    # Override 2: Patch the global _db_helper singleton in dependencies.py so
    # the lifespan's direct call to get_db_helper() returns our no-op mock.
    # This prevents any attempt to open a connection pool during TestClient startup.
    with patch("dependencies._db_helper", mock_db_helper):
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client

    # Restore real wiring after the test so other test modules are not affected.
    app.dependency_overrides.clear()
