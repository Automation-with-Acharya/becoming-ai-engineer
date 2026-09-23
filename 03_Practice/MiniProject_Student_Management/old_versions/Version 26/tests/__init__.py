"""
tests/ package — Day 033: Automated Testing.

Three test categories live here:

  unit/        → Pure Python tests; no database, no network, no Docker.
                 The StudentRepository is replaced with a MagicMock.

  integration/ → Tests that talk to a real (local) PostgreSQL instance.
                 Uses a temporary test table to avoid touching development data.

  api/         → HTTP-level tests via FastAPI's TestClient.
                 Uses dependency_overrides to inject a fake service so no
                 database connection is required.
"""
