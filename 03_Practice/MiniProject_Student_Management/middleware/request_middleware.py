"""
Middleware Module — Day 016 Exercises.

Contains five simple middleware functions registered on the FastAPI application:

  Exercise 1 — Log Incoming Requests   : Prints the HTTP method and path on every request.
  Exercise 2 — Measure Execution Time  : Measures round-trip duration and adds it as a header.
  Exercise 3 — Console Request Logging : Prints method, path and final HTTP status code.
  Exercise 4 — CORS                    : Allows requests from http://localhost:5173.
  Exercise 5 — Middleware Order Demo   : Two sequential middleware to observe pipeline ordering.

All middleware use Starlette's BaseHTTPMiddleware for simplicity and readability.
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


# ──────────────────────────────────────────────────────────────────────────────
# Exercise 1 — Log Incoming Requests
# ──────────────────────────────────────────────────────────────────────────────

class LogIncomingRequestMiddleware(BaseHTTPMiddleware):
    """
    Exercise 1: Log every incoming request's HTTP method and URL path.

    Output example:
        Incoming Request:
        GET /students
    """

    async def dispatch(self, request: Request, call_next):
        print(f"\nIncoming Request:")
        print(f"{request.method} {request.url.path}")
        response = await call_next(request)
        return response


# ──────────────────────────────────────────────────────────────────────────────
# Exercise 2 — Measure Execution Time
# ──────────────────────────────────────────────────────────────────────────────

class ExecutionTimeMiddleware(BaseHTTPMiddleware):
    """
    Exercise 2: Measure how long each request takes and attach the duration as a
    custom response header (X-Process-Time-Ms).

    Output example:
        Request completed in 18 ms
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration_ms = round((time.time() - start_time) * 1000)
        print(f"Request completed in {duration_ms} ms")
        response.headers["X-Process-Time-Ms"] = str(duration_ms)
        return response


# ──────────────────────────────────────────────────────────────────────────────
# Exercise 3 — Console Request Logging
# ──────────────────────────────────────────────────────────────────────────────

class ConsoleRequestLogMiddleware(BaseHTTPMiddleware):
    """
    Exercise 3: Log the completed request in a concise one-liner showing method,
    path, and final HTTP status code.

    Output example:
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
        print(f"{request.method} {request.url.path} -> {response.status_code} {phrase}")
        return response


# ──────────────────────────────────────────────────────────────────────────────
# Exercise 5 — Middleware Order Demo (two middleware, A then B)
# ──────────────────────────────────────────────────────────────────────────────

class MiddlewareOrderDemoA(BaseHTTPMiddleware):
    """
    Exercise 5 — Middleware A (registered first, but runs last due to stack order).

    Demonstrates that FastAPI middleware is a LIFO stack:
      - The LAST middleware added with add_middleware() runs FIRST on the request.
      - On the response it unwinds in reverse, so A sees the response last.

    Output example (request side):
        [Middleware A] → Request entering
        ...
        [Middleware A] ← Response leaving
    """

    async def dispatch(self, request: Request, call_next):
        print("[Middleware A] → Request entering")
        response = await call_next(request)
        print("[Middleware A] ← Response leaving")
        return response


class MiddlewareOrderDemoB(BaseHTTPMiddleware):
    """
    Exercise 5 — Middleware B (registered second, runs first on request).

    Output example:
        [Middleware B] → Request entering
        ...
        [Middleware B] ← Response leaving
    """

    async def dispatch(self, request: Request, call_next):
        print("[Middleware B] → Request entering")
        response = await call_next(request)
        print("[Middleware B] ← Response leaving")
        return response
