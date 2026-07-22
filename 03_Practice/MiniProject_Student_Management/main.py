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
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from routers.students import router as student_router
from dependencies import get_db_helper


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
    print("[Lifespan Startup] Connecting to PostgreSQL...")
    db_helper.connect()
    print("[Lifespan Startup] Connected and verified table schemas successfully.")
    
    yield  # Hand over control to the FastAPI application execution
    
    # ------------------ SHUTDOWN ------------------
    # Safely close connection when the server is stopped
    print("[Lifespan Shutdown] Closing database connections...")
    db_helper.close()
    print("[Lifespan Shutdown] PostgreSQL connection closed.")


# Instantiate the FastAPI application with custom metadata and lifespan hook.
app = FastAPI(
    title="Student Management REST API",
    description="A FastAPI-based REST API demonstrating Clean Architecture, Dependency Injection, and proper HTTP error handling.",
    version="1.0.0",
    lifespan=lifespan
)

# Register routers.
app.include_router(student_router)


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
    print(f"[Exception Handled] ValueError occurred during API request: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Bad Request",
            "message": str(exc),
            "detail": "The request payload failed schema validation checks."
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
    return {
        "message": "Welcome to the Student Management REST API!",
        "documentation": "/docs",
        "health": "healthy"
    }
