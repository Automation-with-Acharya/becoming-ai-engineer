# Use a small, official Python runtime image as the build base.
# 'python:3.14-slim' includes Python 3.14 and keeps the image size minimal.
FROM python:3.14-slim

# Prevent Python from writing .pyc files to disk and force stdout/stderr to be unbuffered.
# This is useful in Docker logs and avoids unnecessary file generation inside the container.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container. All subsequent commands run from /app.
WORKDIR /app

# Copy only the dependency file first, so Docker can cache pip install results when requirements.txt does not change.
COPY requirements.txt .

# Upgrade pip and install Python dependencies from requirements.txt.
# --no-cache-dir prevents pip from storing packages in cache, which keeps the image smaller.
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code into the container.
# This includes app.py, main.py, modules, routers, config, and any other project files.
COPY . .

# Declare that the container listens on port 8000 at runtime.
EXPOSE 8000

# Define the default command to run the FastAPI app with Uvicorn when the container starts.
# 0.0.0.0 binds to all network interfaces inside the container so Docker can route traffic.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
