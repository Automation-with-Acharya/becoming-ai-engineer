from fastapi import FastAPI

try:
    from .routers.students import router as students_router
except ImportError:  # pragma: no cover - allows running the module directly
    from routers.students import router as students_router

app = FastAPI(title="Student Management API")
app.include_router(students_router)
