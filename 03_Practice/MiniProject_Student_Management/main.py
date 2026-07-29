"""
Main Application Entry Point.

This script bootstraps and configures the FastAPI web application. It integrates the routing
layer, registers database lifecycle hooks (lifespan), and defines custom HTTP error handlers.

Why is a lifespan handler required here?
-----------------------------------------
1. Startup Actions: We need to connect to the PostgreSQL database when the server starts up.
   `db_helper.connect()` initializes the connection and verifies/creates the database schema.
2. Shutdown Actions: When the server stops, we must clean up and release connection resources
   by calling `db_helper.close()`. This prevents socket leaks and dangling PostgreSQL backends.
3. Lifespan Efficiency: Managing the connection globally inside a lifespan block ensures that 
   the web server retains a persistent connection (or pool of connections) for all incoming API 
   requests, rather than incurring the overhead of connecting/disconnecting on every single request.
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

# ── Day 017 Exercise 1–5: Import the central logger (configures FileHandler + StreamHandler)
from logger_config import get_logger

logger = get_logger(__name__)


# Define the lifespan context manager to coordinate application startup and shutdown events.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Asynchronous lifespan context manager managing resources for the FastAPI application.
    Executes database startup connection and shutdown cleanup safely.
    """
    # ------------------ STARTUP ------------------
    # Retrieve the database helper dependency and establish connection
    db_helper = get_db_helper()
    logger.info("[Lifespan Startup] Connecting to PostgreSQL...")
    try:
        db_helper.connect()
        logger.info("[Lifespan Startup] Connected and verified table schemas successfully.")
    except Exception:
        # Exercise 4: logger.exception() records the full stack trace automatically
        logger.exception("[Lifespan Startup] FAILED to connect to PostgreSQL database.")
        raise  # Re-raise so FastAPI aborts startup

    yield  # Hand over control to the FastAPI application execution

    # ------------------ SHUTDOWN ------------------
    # Safely close connection when the server is stopped
    logger.info("[Lifespan Shutdown] Closing database connections...")
    try:
        db_helper.close()
        logger.info("[Lifespan Shutdown] PostgreSQL connection closed.")
    except Exception:
        logger.exception("[Lifespan Shutdown] Error occurred while closing the database connection.")


# Instantiate the FastAPI application with custom metadata and lifespan hook.
app = FastAPI(
    title="Student Management REST API",
    description=(
        "A FastAPI-based REST API demonstrating Clean Architecture, Dependency Injection, proper HTTP error handling, JWT authentication, Middleware implementation, application-wide logging, and Global Exception Handling.\n\n"
        
        "**Demo credentials:** `admin/admin123` · `alice/student456` · `bob/teacher789`"
    ),
    version="5.0.0",
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

logger.info("FastAPI application initialised — routers and middleware registered.")


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
