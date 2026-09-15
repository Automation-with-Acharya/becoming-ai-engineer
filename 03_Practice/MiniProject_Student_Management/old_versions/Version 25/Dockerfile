# Use a small, official Python runtime image as the build base.
# 'python:3.14-slim' includes Python 3.14 and keeps the image size minimal.
# This is a production-suitable base — no dev tools, no package manager cache.
FROM python:3.14-slim

# Prevent Python from writing .pyc bytecode files to disk.
# PYTHONDONTWRITEBYTECODE=1 → no __pycache__ in the image (keeps it clean).
# PYTHONUNBUFFERED=1        → stdout/stderr are flushed immediately (important
#                             for real-time log streaming in Docker).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container.
# All subsequent COPY, RUN, and CMD instructions run relative to /app.
WORKDIR /app

# Copy only the dependency manifest first.
# Docker caches this layer independently — if requirements.txt is unchanged,
# the expensive 'pip install' step below is served from cache on rebuilds.
COPY requirements.txt .

# Upgrade pip and install all Python dependencies.
# --no-cache-dir tells pip not to store packages in its local cache directory,
# which keeps the final image size smaller (no redundant cached wheels).
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Day 029 — Non-root user (Exercise 3)
# Running as root inside a container is a security risk: if an attacker escapes
# the container, they inherit root-level privileges on the host kernel.
# Creating a dedicated non-root user (appuser) limits the blast radius of any
# container escape or remote code execution vulnerability.
#
# useradd is the low-level, non-interactive utility (always silent, no prompts).
# Flags used:
#   --system          : create a system account (no password, no aging info)
#   --no-create-home  : no /home/appuser needed; the app lives at /app
#   --shell /bin/false: no interactive login shell for this user
#   --group           : create a matching group (appuser:appuser)
# chown -R: transfer ownership of /app to appuser so the running process can
# write to ./logs (the bind-mounted log directory).
RUN useradd --system --no-create-home --shell /bin/false appuser \
    && chown -R appuser:appuser /app

# Switch to the non-root user for all subsequent instructions and at runtime.
# Every command after this line (including CMD) runs as appuser, not root.
USER appuser

# Copy the entire application source code into /app.
# .dockerignore excludes: .git, .venv, __pycache__, logs/, .env,
# .vscode/, Dockerfile, and other dev-only artifacts — keeping the image lean
# and ensuring no secrets or editor config reach the container.
# This COPY runs as the build user (root during build), but the files are
# already owned by appuser from the chown above.
COPY --chown=appuser:appuser . .

# Declare that the container listens on port 8000 at runtime.
# This is metadata only — it does not publish the port. Publishing is done
# via the 'ports:' key in compose.yaml (8000:8000).
EXPOSE 8000

# Define the default command to start the FastAPI app with Uvicorn.
# --host 0.0.0.0  → bind to all network interfaces inside the container
#                   so Docker's bridge network can route traffic to it.
# --port 8000     → match the EXPOSE declaration above.
# No --reload     → production: reload is disabled for stability.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
