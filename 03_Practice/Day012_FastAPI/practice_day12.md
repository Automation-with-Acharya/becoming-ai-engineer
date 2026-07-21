# Day 12 - FastAPI Practice

## Exercise 1

- Create an APIRouter.
- Example endpoint:
  - `GET /students`

## Exercise 2

- Move all student endpoints into:
  - `routers/students.py`

## Exercise 3

- Create a service method:
  - `get_all_students()`
- The router should call the service, not the repository directly.

## Exercise 4

- Use `Depends()` to inject the service into the route handler.
- The goal is to understand the concept, even if the implementation is simple.

## Exercise 5

- Run the application and verify:
  - Swagger UI works.
  - Routes are discovered.
  - Endpoints behave exactly as before.
