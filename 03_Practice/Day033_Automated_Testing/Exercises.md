# Automated Testing Exercises

## Exercise 1: Inspect the Current Application

Start by identifying:

- Router
- Service
- Repository

Map the request flow:

```text
POST /students
        |
    Router
        |
    Service
        |
 Repository
        |
 Database
```

Then find:

- Authentication
- Exception handling
- Configuration

You are going to decide where tests belong based on this architecture.

## Exercise 2: Create the Test Structure

Create a professional test structure such as:

```text
tests/
├── conftest.py
├── unit/
│   ├── test_student_service.py
│   └── ...
├── integration/
│   ├── test_student_repository.py
│   └── ...
└── api/
        ├── test_student_routes.py
        └── ...
```

You do not need dozens of tests today.

The objective is to understand why different tests exist.

## Exercise 3: Your First Service Unit Test

Suppose your Service depends on a Repository:

```text
StudentService
            |
StudentRepository
```

Create a test where the Repository is replaced with a mock or fake.

Conceptually:

```python
mock_repository = Mock()
```

Then the flow becomes:

```text
Test
    |
StudentService
    |
Mock Repository
    |
Controlled result
```

For example, configure the mock repository so:

```text
get_by_id(1)
        |
returns Student(...)
```

Then verify that:

```python
service.get_student(1)
```

returns the expected result.

## Exercise 4: Test Not Found

This connects directly to the question you asked on Day 18.

Your Service might behave like this:

```text
Repository
        |
    None
        |
Service raises StudentNotFound
```

Write a test proving that behavior.

Conceptually:

```python
mock_repository.get_by_id.return_value = None
```

Then:

```python
with pytest.raises(StudentNotFound):
        service.get_student(999)
```

Now we have a concrete contract:

- Repository says: "not found"
- Service says: "StudentNotFound"
- Global FastAPI handler says: "404 response"

This is exactly the kind of separation Clean Architecture gives us.

## Exercise 5: Test Business Rules Without PostgreSQL

This is the most important exercise of today.

Make PostgreSQL disappear from the test.

```text
                         UNIT TEST

                StudentService
                            |
                Mock Repository
                            |
                            X
                    PostgreSQL
```

The test should run without:

- Docker
- PostgreSQL
- Network access
- Database credentials

This is what makes it a unit test of the Service layer.

## Exercise 6: Verify Repository Interaction

Do not only test the returned value.

Also test:

- Was the Repository called?
- Was it called with the right argument?
- Was it called the expected number of times?

For example:

```python
mock_repository.get_by_id.assert_called_once_with(1)
```

This helps establish the interaction contract between Service and Repository.

But do not over-test implementation details.

The goal is to verify meaningful behavior, not make tests fragile.

## Exercise 7: Repository Test

Now create a small integration-style Repository test that actually talks to PostgreSQL.

The architecture becomes:

```text
Test
    |
Repository
    |
Real Database Helper
    |
PostgreSQL
```

Unlike the Service test:

```text
Service
    |
Mock Repository
```

This one intentionally exercises the real database interaction.

Use an isolated test database, schema, or environment so that tests do not destroy your normal development data.

## Exercise 8: API Test with FastAPI TestClient

Now test one HTTP endpoint.

Conceptually:

```text
TestClient
        |
FastAPI
        |
 Router
        |
 Service
```

For example:

```python
response = client.get("/students/1")
```

Then assert:

```python
assert response.status_code == 200
```

And inspect:

```python
response.json()
```

This gives us our first actual API-level automated test.

## Exercise 9: Dependency Override

Now connect today's work directly to Day 12.

Suppose FastAPI normally uses the real `StudentService` during production.

For a test, override it:

```text
FastAPI
        |
Dependency Override
        |
Fake / Mock Service
```

FastAPI's testing documentation specifically supports dependency overrides for replacing production dependencies during tests.

This is the point where you should have the realization:

> Dependency Injection was not just about cleaner code. It created a seam where testing can replace real infrastructure with controlled test doubles.

That is the real engineering value.

## Exercise 10: Test an Exception / 404

Now test the API behavior when a student does not exist.

The flow should be:

```text
GET /students/999999
                |
            Router
                |
            Service
                |
 StudentNotFound
                |
Global Exception Handler
                |
         HTTP 404
```

Your test should verify:

- Status is `404`.
- Response body matches the expected error structure.

This connects:

```text
Day 13
CRUD + HTTP Status Codes
                |
Day 18
Global Exception Handling
                |
Day 33
Automated Testing
```

## Exercise 11: Run the Entire Test Suite

Run:

```bash
pytest
```

Then run with more visibility:

```bash
pytest -v
```

Your mental model should be:

```text
pytest
    |
Discover tests
    |
Execute fixtures
    |
Run test functions
    |
Assertions
    |
PASS / FAIL
```
