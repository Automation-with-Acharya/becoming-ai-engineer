"""
Application Runner Module.

Acts as the entry point wrapper to launch the FastAPI web application using Uvicorn.
"""

import uvicorn

if __name__ == "__main__":
    # Start the Uvicorn ASGI server programmatically.
    # Enables hot-reloading (reload=True) which restarts the server automatically when code files change.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
