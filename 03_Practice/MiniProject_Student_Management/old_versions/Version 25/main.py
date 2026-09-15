"""
Main Application Entry Point.

This script bootstraps and configures the FastAPI web application. It integrates the routing
layer, registers database lifecycle hooks (lifespan), and defines custom HTTP error handlers.

Why is a lifespan handler required here?
-----------------------------------------
1. Startup Actions: We need to open a connection pool to PostgreSQL when the server starts.
   `db_helper.open_pool()` creates min_size ready connections and verifies/creates the schema.
2. Shutdown Actions: When the server stops, `db_helper.close_pool()` cleanly drains and closes
   all pool connections, preventing socket leaks and dangling PostgreSQL backends.
3. Pool Efficiency: A pool keeps multiple connections open so concurrent requests never wait for
   a fresh TCP handshake + TLS negotiation. Connections are borrowed per-operation and returned
   immediately, enabling true parallelism up to max_size simultaneous DB queries.
   Day 021 Exercise 4: open_pool() / close_pool() are now the lifespan actions.
"""

from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routers.students import router as student_router
from routers.auth import router as auth_router
from dependencies import get_db_helper
from middleware.request_middleware import (
    LogIncomingRequestMiddleware,
    ExecutionTimeMiddleware,
    ConsoleRequestLogMiddleware
)
from exceptions import StudentNotFoundException

# Day 019 Exercise 3: Import settings so app metadata is read from .env
from config import settings

# ── Day 017 Exercise 1–5: Import the central logger (configures FileHandler + StreamHandler)
from logger_config import get_logger

logger = get_logger(__name__)


# Define the lifespan context manager to coordinate application startup and shutdown events.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Day 021 Exercise 4: Async lifespan managing the connection pool lifecycle.

    Startup  — opens the psycopg_pool.ConnectionPool (min_size connections pre-created).
    Shutdown — closes all pool connections cleanly before the process exits.
    """
    # ------------------ STARTUP ------------------
    db_helper = get_db_helper()
    logger.info(
        "[\U0001f7e2 Lifespan Startup] Opening connection pool (min=%d, max=%d)...",
        settings.db_pool_min_size, settings.db_pool_max_size,
    )
    try:
        db_helper.open_pool()
        logger.info("[\U0001f7e2 Lifespan Startup] Pool open and schema verified.")
    except Exception:
        logger.exception("[\U0001f7e2 Lifespan Startup] FAILED to open connection pool.")
        raise  # Re-raise so FastAPI aborts startup

    yield  # Hand over control to the FastAPI application execution

    # ------------------ SHUTDOWN ------------------
    logger.info("[\U0001f534 Lifespan Shutdown] Closing connection pool...")
    try:
        db_helper.close_pool()
        logger.info("[\U0001f534 Lifespan Shutdown] Connection pool closed.")
    except Exception:
        logger.exception("[\U0001f534 Lifespan Shutdown] Error while closing the connection pool.")


# Day 019 Exercise 3: App metadata now sourced from settings (.env) — no more hardcoded strings.
app = FastAPI(
    title=settings.app_name,
    description=(
        "A FastAPI-based REST API demonstrating Clean Architecture, Dependency Injection, "
        "proper HTTP error handling, JWT authentication, Middleware implementation, "
        "application-wide logging, Global Exception Handling, and Environment-based Configuration.\n\n"
        "**Demo credentials:** `admin/admin123` · `alice/student456` · `bob/teacher789`"
    ),
    version=settings.app_version,
    lifespan=lifespan
)


# ──────────────────────────────────────────────────────────────────────────────
# Day 016 Middleware Registration
# ──────────────────────────────────────────────────────────────────────────────
# NOTE: FastAPI processes middleware in LIFO (Last In, First Out) order.
# The last middleware added here runs FIRST on incoming requests.
# Reading the list top-to-bottom = order of response unwinding (outermost last).

# Exercise 4 — CORS: allow requests from the Vite dev-server origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exercise 1 — Log incoming request method + path.
app.add_middleware(LogIncomingRequestMiddleware)

# Exercise 2 — Measure execution time and attach X-Process-Time-Ms header.
app.add_middleware(ExecutionTimeMiddleware)

# Exercise 3 — One-line console log after each completed request.
app.add_middleware(ConsoleRequestLogMiddleware)

# Register routers.
app.include_router(student_router)
app.include_router(auth_router)

# Day 019 Exercise 3: Log active config at startup so the profile is visible in terminal + log file.
logger.info(
    "FastAPI application initialised — name='%s' version=%s debug=%s log_level=%s. And routers and middleware are now registered.",
    settings.app_name, settings.app_version, settings.debug, settings.log_level,
)


# ----------------------------------------------------
# HTTP Custom Exception & Global Error Handling
# ----------------------------------------------------

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """
    Global exception handler for python's built-in ValueError.
    
    Why is this required?
    --------------------
    In our clean architecture, validation logic (in schemas) and business logic (in services)
    raise raw Python exceptions like `ValueError` when parameters are invalid (e.g. empty student name).
    Instead of adding try-except blocks inside every router path operation, this global handler
    catches all ValueErrors thrown anywhere in the request context and formats them into a clean,
    standardized HTTP 400 Bad Request JSON response for the API client.
    """
    # Day 017 Exercise 3: Replace print() with logger.warning() for handled validation errors
    logger.warning(
        "[Exception Handled] ValueError on %s %s — %s",
        request.method,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "detail": "The request payload failed schema validation checks."
        }
    )


# ───────────────────────────────────────────────────────────────────────────────
# Day 018 Exercise 3 + 4: Global handler for StudentNotFoundException
# ───────────────────────────────────────────────────────────────────────────────

@app.exception_handler(StudentNotFoundException)
async def student_not_found_exception_handler(request: Request, exc: StudentNotFoundException):
    """
    Day 018 Exercise 3: Global handler for StudentNotFoundException.

    Why global instead of per-route?
    --------------------------------
    Every route that looks up or deletes a student would otherwise need its own try/except.
    A single global handler keeps all route functions clean and ensures a consistent
    404 JSON response shape across the entire API.

    Day 018 Exercise 4: Logs the exception via the centralized logger (WARNING level,
    because a missing student is a client error, not a server fault).
    """
    # Day 018 Exercise 4: Log via centralized logger (not print!)
    logger.warning(
        "[Exception Handled] StudentNotFoundException on %s %s — student_id=%d",
        request.method,
        request.url.path,
        exc.student_id,
    )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": str(exc),          # e.g. "Student with ID 42 not found."
            "student_id": exc.student_id,
        }
    )


# ───────────────────────────────────────────────────────────────────────────────
# Day 018: Catch-all fallback for any other unhandled exception
# ───────────────────────────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """
    Day 018: Catch-all global exception handler.

    Catches any exception that was NOT already handled by a more specific handler above.
    Instead of the client receiving a raw FastAPI/Starlette 500 HTML error page, they get
    a consistent, informative JSON response.  The full exception detail is logged server-side
    for diagnosis but is NOT exposed to the client (security best practice).

    IMPORTANT: More-specific handlers (ValueError, StudentNotFoundException) registered above
    take precedence over this handler for their respective exception types.  Python/FastAPI
    evaluates handlers from most-specific to least-specific.
    """
    # Day 018 Exercise 4: logger.exception() captures the full stack trace in the log file
    logger.exception(
        "[Unhandled Exception] %s on %s %s — %s",
        type(exc).__name__,
        request.method,
        request.url.path,
        str(exc),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "exception_type": type(exc).__name__,  # class name aids debugging without leaking internals
        }
    )


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Root Endpoint",
    tags=["General"]
)
def read_root():
    """
    Root API endpoint providing basic app metadata and access information.
    """
    logger.debug("Root endpoint accessed.")
    return {
        "message": "Welcome to the Student Management REST API!",
        "documentation": "/docs",
        "health": "healthy"
    }
