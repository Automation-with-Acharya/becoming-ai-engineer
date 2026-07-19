# Day 11 FastAPI Practice

## Exercise 1

Create a `Student` model:

```python
class Student(BaseModel):
    name: str
    age: int
    city: str
```

## Exercise 2

Create a GET endpoint:

`GET /students`

Returns all students.

## Exercise 3

Create a GET endpoint by ID:

`GET /students/{student_id}`

## Exercise 4

Create a POST endpoint that accepts the `Student` model.

Return:

```json
{
  "message": "Student Added"
}
```

## Exercise 5

Add a query parameter for city filtering.

Example:

`/students?city=Ahmedabad`

Return only students from that city.

## Exercise 6

Observe validation.

Try:

```json
{
  "name": 123,
  "age": "abc"
}
```

See FastAPI reject it automatically.

This is one of FastAPI's biggest strengths.
