"""
Middleware Module — Day 016 Exercises.

Contains five simple middleware functions registered on the FastAPI application:

  Exercise 1 — Log Incoming Requests   : Logs the HTTP method and path on every request.
  Exercise 2 — Measure Execution Time  : Measures round-trip duration and adds it as a header.
  Exercise 3 — Console Request Logging : Logs method, path and final HTTP status code.
  Exercise 4 — CORS                    : Allows requests from http://localhost:5173.
  Exercise 5 — Middleware Order Demo   : Two sequential middleware to observe pipeline ordering.

All middleware use Starlette's BaseHTTPMiddleware for simplicity and readability.

Day 017 Update: All print() statements replaced with structured logger calls.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Exercise 3: Import centralized logger instead of using print()
from logger_config import get_logger

logger = get_logger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Exercise 1 — Log Incoming Requests
# ──────────────────────────────────────────────────────────────────────────────

class LogIncomingRequestMiddleware(BaseHTTPMiddleware):
    """
    Exercise 1: Log every incoming request's HTTP method and URL path.

    Log example:
        Incoming Request: GET /students
    """

    async def dispatch(self, request: Request, call_next):
        # Exercise 3: logger.info() replaces print() for request logging
        logger.info("Incoming Request: %s %s", request.method, request.url.path)
        response = await call_next(request)
        return response


# ──────────────────────────────────────────────────────────────────────────────
# Exercise 2 — Measure Execution Time
# ──────────────────────────────────────────────────────────────────────────────

class ExecutionTimeMiddleware(BaseHTTPMiddleware):
    """
    Exercise 2: Measure how long each request takes and attach the duration as a
    custom response header (X-Process-Time-Ms).

    Log example:
        Request completed in 18 ms
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000)
        # Exercise 3: logger.debug() for high-frequency timing details (DEBUG level →
        # visible in log file but suppressed on console to keep output clean)
        logger.debug(
            "Execution time: %s %s → %d ms",
            request.method,
            request.url.path,
            duration_ms,
        )
        response.headers["X-Process-Time-Ms"] = str(duration_ms)
        return response


# ──────────────────────────────────────────────────────────────────────────────
# Exercise 3 — Console Request Logging
# ──────────────────────────────────────────────────────────────────────────────

class ConsoleRequestLogMiddleware(BaseHTTPMiddleware):
    """
    Exercise 3: Log the completed request in a concise one-liner showing method,
    path, and final HTTP status code.

    Log example:
        GET /students -> 200 OK
    """

    # Standard HTTP status reason phrases for common codes.
    STATUS_PHRASES = {
        200: "OK", 201: "Created", 204: "No Content",
        400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
        404: "Not Found", 422: "Unprocessable Entity",
        500: "Internal Server Error",
    }

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        phrase = self.STATUS_PHRASES.get(response.status_code, "")
        status_code = response.status_code

        # Exercise 3: Use logger.warning() for 4xx/5xx, logger.info() for 2xx/3xx
        if status_code >= 500:
            logger.error(
                "%s %s -> %d %s",
                request.method, request.url.path, status_code, phrase,
            )
        elif status_code >= 400:
            logger.warning(
                "%s %s -> %d %s",
                request.method, request.url.path, status_code, phrase,
            )
        else:
            logger.info(
                "%s %s -> %d %s",
                request.method, request.url.path, status_code, phrase,
            )

        return response

