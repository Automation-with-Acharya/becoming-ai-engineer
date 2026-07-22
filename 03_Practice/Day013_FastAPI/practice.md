# FastAPI Student Management Exercises

## Exercise 1

- Implement `GET /students`
- Return all students

## Exercise 2

- Implement `GET /students/{id}`
- If not found, raise:

```python
HTTPException(
    status_code=404,
    detail="Student not found"
)
```

## Exercise 3

- Implement `POST /students`
- Return `201 Created`

## Exercise 4

- Implement `PUT /students/{id}`
- Update student
- Return `200 OK`

## Exercise 5

- Implement `DELETE /students/{id}`
- If deleted, return `204 No Content`
- If student doesn't exist, return `404`

## Exercise 6

- Test every endpoint in Swagger
- Verify:
  - valid requests
  - invalid IDs
  - missing body
  - duplicate IDs (if applicable)
- Observe the status code each time.
