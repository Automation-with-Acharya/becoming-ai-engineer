# Day 033 — Repository Improvements & Automated Testing

> **Project ₹50L — Engineering Handbook**  
> **Phase:** Phase 1 — Core AI/GenAI & Backend Engineering  
> **Week:** Week 5 — Advanced SQL, Repository Improvements & Testing  
> **Focus:** Repository abstraction, dependency injection, unit testing, integration testing, FastAPI endpoint testing, pytest fixtures, mocks

---

## 1. Day Objective

Day 33 moves the Student Management Backend from **working code** toward **engineering-quality code**.

The central question is:

> **How do we make backend code easy to change and difficult to accidentally break?**

The answer is not simply “write tests.” The deeper engineering answer is to design boundaries between responsibilities so that each layer can be tested at the right level.

By the end of this topic, the mental model should be:

```text
                    HTTP Request
                          │
                          ▼
                  ┌──────────────┐
                  │    Router    │
                  │ HTTP concern │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   Service    │
                  │ Business     │
                  │ logic        │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │ Repository   │
                  │ Data access  │
                  └──────┬───────┘
                         │
                         ▼
                    PostgreSQL
```

Testing then becomes:

```text
Router      → API / endpoint tests
Service     → Unit tests + mocked repository
Repository  → Integration tests + real PostgreSQL
```

That separation is one of the foundations of maintainable backend systems.

---

# 2. Why This Day Matters for the ₹50L Target

At junior level, the common question is:

> “Can you write an API?”

At senior level, the question becomes:

> “Can you design an API that another engineer can safely modify six months later?”

And at staff/principal level:

> “Can the organization change one part of the system without destabilizing the rest?”

Automated testing and repository abstraction directly support that third level of thinking.

A production system is never judged only by whether it works today. It is judged by whether engineers can confidently change it tomorrow.

---

# 3. The Big Picture — Testing Is About Boundaries

A useful model is to think of a test as answering one question at one boundary.

| Test level | Main question | Typical dependency | Speed |
|---|---|---|---|
| Unit test | Does this business logic behave correctly? | Mock/fake dependencies | Very fast |
| Integration test | Does this component work with the real dependency? | Real PostgreSQL | Slower |
| API test | Does the application expose the correct HTTP behavior? | FastAPI TestClient | Medium |
| End-to-end test | Does the complete system work as a user experiences it? | Real services | Slowest |

The goal is **not** to make every test a full end-to-end test.

Instead:

```text
                         More isolated
                              ▲
                              │
                       Unit tests
                              │
                   Integration tests
                              │
                      API tests
                              │
                    End-to-end tests
                              │
                              ▼
                        More realistic
```

A healthy test suite normally contains many fast tests and fewer expensive tests.

---

# 4. Repository Pattern — Why It Exists

The Repository Pattern creates a boundary around data access.

Without a repository, business logic can become tightly coupled to SQL/database code:

```python
class StudentService:
    def get_student(self, student_id: int):
        result = db.execute(
            "SELECT * FROM students WHERE id = %s",
            (student_id,)
        )
        return result.fetchone()
```

Now the service knows:

- database technology
- SQL
- connection mechanics
- result handling

That makes the service harder to test.

With a repository:

```python
class StudentRepository:
    def get_by_id(self, student_id: int):
        # database-specific work
        ...


class StudentService:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def get_student(self, student_id: int):
        return self.repository.get_by_id(student_id)
```

The service now depends on an abstraction of **what it needs**, not on the implementation details of **how the database works**.

---

# 5. Dependency Injection — The Key Enabler

Dependency Injection (DI) means that an object receives the dependencies it needs instead of constructing them internally.

Bad for testability:

```python
class StudentService:
    def __init__(self):
        self.repository = StudentRepository()
```

The service has hard-coded construction.

Better:

```python
class StudentService:
    def __init__(self, repository):
        self.repository = repository
```

Now production code can provide the real repository:

```text
StudentService(ProductionStudentRepository)
```

while a unit test can provide a mock:

```text
StudentService(MockStudentRepository)
```

FastAPI also provides a dependency injection system, which makes replacing dependencies during tests especially useful. citehttps://fastapi.tiangolo.com/tutorial/dependencies/https://fastapi.tiangolo.com/advanced/testing-dependencies/

---

# 6. pytest — The Testing Framework

`pytest` is a Python testing framework designed around straightforward test functions, assertions, fixtures, and a rich plugin ecosystem.

A basic test looks like:

```python
def test_addition():
    result = 2 + 3
    assert result == 5
```

Run:

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

The standard naming convention is important:

```text
test_*.py
*_test.py
```

and test functions commonly begin with:

```text
test_
```

This allows pytest to discover tests automatically.

---

# 7. Assertions — Test Behavior, Not Implementation

A good test generally follows:

```text
Arrange → Act → Assert
```

Example:

```python
def test_student_service_returns_student():
    # Arrange
    repository = FakeStudentRepository()
    repository.student = {"id": 1, "name": "Mayank"}

    service = StudentService(repository)

    # Act
    result = service.get_student(1)

    # Assert
    assert result["id"] == 1
    assert result["name"] == "Mayank"
```

The important part is not the exact arrangement. It is that the test states the behavior clearly.

Avoid writing tests whose only purpose is to mirror implementation details.

---

# 8. Testing Exceptions

Backend logic frequently has expected failure behavior.

For example, a service may raise a not-found exception:

```python
class StudentNotFoundError(Exception):
    pass
```

Test it explicitly:

```python
import pytest


def test_get_student_raises_when_missing():
    service = StudentService(FakeStudentRepository())

    with pytest.raises(StudentNotFoundError):
        service.get_student(999)
```

This is valuable because it locks in an important business rule:

```text
Missing student
      │
      ▼
Service detects absence
      │
      ▼
StudentNotFoundError
```

A router can then translate that domain-level outcome into HTTP behavior such as `404 Not Found`.

That separation keeps HTTP concerns out of the service layer.

---

# 9. pytest Fixtures

A fixture provides reusable test setup.

Example:

```python
import pytest


@pytest.fixture
def student():
    return {
        "id": 1,
        "name": "Mayank",
        "city": "Ahmedabad",
    }


def test_student_name(student):
    assert student["name"] == "Mayank"
```

The test requests the fixture by naming it as a parameter.

This is conceptually similar to dependency injection:

```text
Test function
      │
      │ requests fixture
      ▼
pytest fixture system
      │
      ▼
Prepared dependency
```

pytest supports fixture scopes including:

- `function`
- `class`
- `module`
- `package`
- `session`

The default scope is `function`, meaning a new fixture instance is normally created for each test using it. citehttps://docs.pytest.org/en/latest/reference/reference.html

---

# 10. `conftest.py` — Shared Test Infrastructure

A common structure is:

```text
tests/
├── conftest.py
├── unit/
├── integration/
└── api/
```

`conftest.py` is useful for fixtures that should be automatically available to tests below that directory.

For example:

```python
# tests/conftest.py

import pytest


@pytest.fixture
def sample_student():
    return {
        "id": 1,
        "name": "Mayank",
    }
```

Then another test file can use it without importing the fixture directly:

```python
def test_student(sample_student):
    assert sample_student["id"] == 1
```

This keeps test setup centralized instead of duplicating infrastructure across test modules.

---

# 11. Mocking — Isolating the Unit Under Test

Suppose the service depends on a repository.

A service unit test usually should not require PostgreSQL.

Instead, replace the repository with a mock.

Python's `unittest.mock` provides `Mock`, `MagicMock`, `patch`, and related tools for replacing collaborators and asserting how they were used. citehttps://docs.python.org/3/library/unittest.mock.html

Example:

```python
from unittest.mock import Mock


def test_service_uses_repository():
    repository = Mock()
    repository.get_by_id.return_value = {
        "id": 1,
        "name": "Mayank",
    }

    service = StudentService(repository)

    result = service.get_student(1)

    assert result["id"] == 1
    repository.get_by_id.assert_called_once_with(1)
```

This test verifies two things:

1. the service returns the expected result
2. the service calls its dependency correctly

---

# 12. `Mock`, `MagicMock`, `patch`, and `side_effect`

## Mock

Use `Mock` for a normal test double.

```python
repository = Mock()
```

## MagicMock

`MagicMock` extends `Mock` with support for many Python magic methods.

```python
from unittest.mock import MagicMock

client = MagicMock()
```

## `return_value`

Specify what a dependency should return:

```python
repository.get_by_id.return_value = {
    "id": 1
}
```

## `side_effect`

Useful for simulating exceptions:

```python
repository.get_by_id.side_effect = RuntimeError("database unavailable")
```

Now the service test can verify how the application reacts to dependency failures.

## `patch`

`patch()` temporarily replaces a target during a test and automatically restores it afterwards. The critical rule is to patch the name **where it is looked up**, not merely where the original object was defined. citehttps://docs.python.org/3/library/unittest.mock.html

---

# 13. Unit Testing the Service Layer

The service is usually an excellent unit-test target because it contains business rules while depending on repositories through a clean boundary.

Typical tests:

```text
StudentService
│
├── get_student()
│   ├── returns student when found
│   └── raises not-found when absent
│
├── create_student()
│   ├── creates valid student
│   └── rejects invalid business state
│
└── delete_student()
    ├── deletes existing student
    └── handles missing student
```

The unit test should substitute the repository with a mock or small fake.

This gives:

```text
Service test
   │
   ├── No Docker dependency
   ├── No PostgreSQL dependency
   ├── No network dependency
   └── Very fast feedback
```

That speed matters when a codebase grows to hundreds or thousands of tests.

---

# 14. Integration Testing the Repository

Repository tests are different.

The repository's job is to communicate correctly with the database, so using a real database is often appropriate.

For example:

```text
Repository test
      │
      ▼
Real PostgreSQL
      │
      ▼
SQL executes
      │
      ▼
Rows returned / persisted
```

A repository integration test can verify:

- SQL correctness
- inserts
- updates
- deletes
- filters
- joins
- transaction behavior
- database constraints
- result mapping

This is especially relevant after Day 30–32, where SQL design and query performance became explicit engineering concerns.

A mock can tell you that:

```python
repository.get_by_id(1)
```

was called.

Only an integration test can tell you that the underlying SQL actually works against PostgreSQL.

---

# 15. API Testing with FastAPI `TestClient`

FastAPI provides `TestClient` for testing application endpoints. It is built on Starlette's test client and uses HTTPX underneath. FastAPI's documentation shows normal pytest functions making requests through the client and asserting on status codes and JSON responses. citehttps://fastapi.tiangolo.com/tutorial/testing/https://fastapi.tiangolo.com/reference/testclient/

Example:

```python
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_student():
    response = client.get("/students/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1
```

This validates the HTTP boundary:

```text
HTTP request
   ↓
Router
   ↓
Dependencies
   ↓
Service
   ↓
Response
```

The test is much closer to how the outside world interacts with your application than a pure service unit test.

---

# 16. Testing HTTP Error Behavior

An API should test failure paths just as intentionally as success paths.

Example:

```python
def test_student_not_found():
    response = client.get("/students/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found"
```

This protects the API contract.

The important distinction is:

```text
Service test:
    Does the business operation raise the correct domain outcome?

API test:
    Does that outcome become the correct HTTP response?
```

That separation gives much more precise failure diagnosis.

---

# 17. FastAPI Dependency Overrides

One of the strongest testing features in FastAPI is `app.dependency_overrides`.

It is a dictionary where:

```text
key   = original dependency
value = test replacement
```

FastAPI then uses the replacement during testing. The official documentation specifically describes this for cases such as replacing external services with deterministic test dependencies. citehttps://fastapi.tiangolo.com/advanced/testing-dependencies/

Conceptually:

```text
Production
---------
Route → Depends(real_repository/provider)

Testing
-------
Route → Depends(test_repository/provider)
```

Example:

```python
app.dependency_overrides[get_student_service] = get_test_student_service
```

After the test, clear overrides:

```python
app.dependency_overrides = {}
```

This cleanup is important because dependency overrides can otherwise leak into later tests. FastAPI's documentation explicitly recommends resetting the overrides dictionary when the override is no longer needed. citehttps://fastapi.tiangolo.com/advanced/testing-dependencies/

---

# 18. The Three-Layer Student Management Test Strategy

For the Student Management Backend, the practical architecture is:

```text
                 ┌─────────────────────┐
                 │      API Tests      │
                 │   TestClient        │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   Service Tests     │
                 │  Mock Repository    │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │ Repository Tests    │
                 │ Real PostgreSQL     │
                 └─────────────────────┘
```

Each layer answers a different question.

### API

> Is the HTTP contract correct?

### Service

> Is the business behavior correct?

### Repository

> Does the data-access implementation actually work?

This is much stronger than writing a single giant test for the complete stack.

---

# 19. Recommended Test Structure

A scalable structure for the project is:

```text
tests/
├── conftest.py
│
├── unit/
│   └── test_student_service.py
│
├── integration/
│   └── test_student_repository.py
│
└── api/
    └── test_student_routes.py
```

The exact project structure may differ, but the architectural separation is the important part.

A useful rule:

> Organize tests around the boundary being validated, not merely around the source file being tested.

---

# 20. What Should Be Mocked?

Mock the things that are external to the behavior you are trying to isolate.

For a service test:

```text
Service = real
Repository = mock
Database = absent
```

For a repository integration test:

```text
Repository = real
PostgreSQL = real
```

For an API test where the objective is the HTTP layer:

```text
FastAPI app = real
Service/dependencies = possibly overridden
Database = possibly absent
```

For an end-to-end test:

```text
Everything = as close to production as practical
```

Do not mock everything simply because you can.

A mock provides isolation, but too much mocking can produce tests that pass while the real system is broken.

---

# 21. The Testing Pyramid

A classic mental model is:

```text
                 /\
                /  \
               / E2E\
              /------\
             /  API   \
            /----------\
           / Integration\
          /--------------\
         /     Unit       \
        /------------------\
```

The bottom layers should normally contain the largest number of tests because they are cheaper and faster.

Think:

```text
Many unit tests
      ↓
Some integration tests
      ↓
Fewer expensive API/E2E tests
```

This is not a rigid law. The correct mix depends on the system, but the cost/isolation trade-off is extremely useful for architectural decisions.

---

# 22. Test Naming

A good test name describes behavior.

Weak:

```python
def test_service_1():
    ...
```

Better:

```python
def test_get_student_returns_student_when_id_exists():
    ...
```

Better still, when concise:

```python
def test_get_student_returns_existing_student():
    ...
```

The goal is that a failed test should tell an engineer approximately what contract was violated.

---

# 23. Failure Diagnostics

A good test suite is also a debugging tool.

Imagine this failure:

```text
FAILED tests/unit/test_student_service.py
```

That points toward business logic.

If instead:

```text
FAILED tests/integration/test_student_repository.py
```

the likely issue is data access, SQL, schema, constraints, or database state.

If:

```text
FAILED tests/api/test_student_routes.py
```

you investigate routing, dependency wiring, serialization, or HTTP behavior.

Good architecture therefore improves not only maintainability but also **failure localization**.

---

# 24. Regression Testing

Every bug that matters should ideally become a test.

Example:

```text
Bug found:
    GET /students/999 returned 500

Fix:
    Service raises StudentNotFoundError
    Router maps it to 404

Regression test:
    test_get_student_returns_404_when_student_missing
```

Now the same bug is harder to reintroduce.

This creates a feedback loop:

```text
Bug
 ↓
Fix
 ↓
Regression test
 ↓
Permanent protection
```

That is one of the highest-value uses of automated testing in real engineering teams.

---

# 25. Repository Improvements — What Good Looks Like

The repository layer should have a narrow responsibility.

Good responsibilities:

- execute database operations
- map database rows to application representations
- encapsulate SQL/data-access details
- handle persistence concerns

Responsibilities that generally belong elsewhere:

- HTTP status codes → router/API layer
- business rules → service layer
- authentication policy → authentication/dependency layer
- user interface → frontend

The cleaner this boundary is, the easier testing becomes.

---

# 26. A Practical Example — Get Student

Production flow:

```text
GET /students/42
      │
      ▼
Student Router
      │
      ▼
Student Service
      │
      ▼
Student Repository
      │
      ▼
PostgreSQL
```

### Unit test

Replace the repository:

```text
Student Router       not involved
Student Service      REAL
Student Repository   MOCK
PostgreSQL           absent
```

### Integration test

```text
Student Router       not involved
Student Service      optional
Student Repository   REAL
PostgreSQL           REAL
```

### API test

```text
HTTP request          REAL through TestClient
FastAPI Router        REAL
Service               real or controlled
Repository            mocked/overridden when isolation is desired
Database              optional depending on test goal
```

The same feature can therefore be tested from several perspectives without duplicating the exact same test.

---

# 27. Clean Architecture Connection

Day 33 is a practical application of a broader architectural principle:

> **Dependencies should point inward toward stable business logic, while infrastructure remains replaceable at the edges.**

A simplified view:

```text
              Infrastructure
        ┌──────────────────────┐
        │ PostgreSQL            │
        │ HTTP                  │
        │ External APIs         │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Adapters / Repository │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Business Logic       │
        │ Service Layer        │
        └──────────────────────┘
```

Testing naturally follows those boundaries.

---

# 28. Enterprise Mapping — ASP.NET Core

The same architectural pattern exists in the .NET ecosystem.

| Python / FastAPI | Typical ASP.NET Core analogue |
|---|---|
| FastAPI Router | Controller / Minimal API endpoint |
| Pydantic schema | DTO / record / model |
| Service layer | Application/service layer |
| Repository | Repository/data-access abstraction |
| FastAPI `Depends` | Built-in .NET DI |
| pytest | xUnit / NUnit / MSTest ecosystem |
| `unittest.mock` | Moq / NSubstitute / similar libraries |
| TestClient | ASP.NET Core integration test client |

The important lesson is not the framework names.

The transferable skill is:

```text
Separation of concerns
        +
Dependency injection
        +
Test doubles
        +
Integration testing
```

That knowledge transfers directly between Python and C# backend environments.

---

# 29. Engineering Sprinkle — Determinism

A test should ideally behave the same way every time when the system under test has not changed.

Avoid unnecessary dependence on:

- wall-clock time
- random values
- external network services
- shared mutable state
- test execution order
- local developer configuration

When randomness is required, make it controllable.

When time matters, inject a clock or use a controllable time source rather than scattering `datetime.now()` throughout business logic.

The broader principle:

> **A deterministic system is easier to test, debug, operate, and scale.**

---

# 30. Engineering Sprinkle — Test Data Isolation

Tests should not silently depend on one another.

Bad:

```text
test_create_student
        ↓
test_get_student_uses_previous_student
```

Good:

```text
test_create_student
        ↓
independent state

test_get_student
        ↓
independent state
```

Fixtures, transactions, setup/teardown, or isolated databases can help establish this property.

The exact strategy depends on project architecture, but the principle remains:

> **Each test should establish the state it needs.**

---

# 31. Engineering Sprinkle — Test the Contract

For a backend engineer, “testing” should not mean checking every line.

Instead test important contracts:

```text
Input
 ↓
Expected business outcome
 ↓
Expected persistence behavior
 ↓
Expected HTTP response
```

A good test suite protects things users and other systems actually depend on.

---

# 32. Common Mistakes

## Mistake 1 — Testing only the happy path

Real bugs often occur at boundaries and failure cases.

Test:

- missing records
- invalid input
- duplicate data
- database failures
- authorization failures
- empty results

## Mistake 2 — Mocking the database in every test

This makes tests fast but can hide SQL and schema problems.

Keep repository integration tests with a real PostgreSQL instance.

## Mistake 3 — Making all tests end-to-end

This often creates a slow, fragile suite.

Use lower-level tests for lower-level behavior.

## Mistake 4 — Testing implementation details

Tests should survive reasonable refactoring.

Test behavior and contracts rather than private implementation steps whenever possible.

## Mistake 5 — Shared mutable test state

One test accidentally changes what another test sees.

Use controlled fixtures and isolated test state.

## Mistake 6 — Forgetting dependency-override cleanup

FastAPI overrides can leak into subsequent tests if not cleared. Reset them after tests that install temporary overrides. citehttps://fastapi.tiangolo.com/advanced/testing-dependencies/

---

# 33. Practical Project Architecture

The Student Management Backend is now moving toward this shape:

```text
student-management/
│
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       └── students.py
│   │
│   ├── services/
│   │   └── student_service.py
│   │
│   ├── repositories/
│   │   └── student_repository.py
│   │
│   ├── schemas/
│   │   └── student.py
│   │
│   └── db/
│       └── ...
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   └── test_student_service.py
│   ├── integration/
│   │   └── test_student_repository.py
│   └── api/
│       └── test_student_routes.py
│
├── Dockerfile
├── compose.yaml
├── .env.example
└── ...
```

This is not about maximizing the number of folders.

The objective is to create clear boundaries that can evolve independently.

---

# 34. How the Student Backend Has Evolved

The learning progression across the recent days is important.

```text
Day 23
Docker fundamentals
        ↓
Day 24
FastAPI containerization
        ↓
Day 25
Compose + multi-container architecture
        ↓
Day 26–29
Health, configuration, networking, deployment hardening
        ↓
Day 30
SQL JOINs + relational design
        ↓
Day 31
EXPLAIN / EXPLAIN ANALYZE
        ↓
Day 32
Indexes + evidence-driven optimization
        ↓
Day 33
Repository boundaries + automated testing
```

Notice the progression:

```text
Run the application
        ↓
Understand the infrastructure
        ↓
Understand the database
        ↓
Optimize the database
        ↓
Make the codebase safe to change
```

That is a strong backend engineering progression.

---

# 35. Interview Questions — Core

### Q1. Why use the Repository Pattern?

To isolate data-access logic from business logic and provide a clean dependency boundary. It can improve testability, maintainability, and replaceability of persistence implementations.

### Q2. Why mock a repository in a service unit test?

Because the test is intended to validate service behavior independently of the database and SQL implementation.

### Q3. Why still have repository integration tests?

Because mocks cannot prove that the SQL, schema, constraints, transactions, and result mapping work against the real database.

### Q4. What is dependency injection?

Supplying a component's dependencies from outside rather than making the component construct those dependencies itself.

### Q5. What is the purpose of a pytest fixture?

To provide reusable, controlled setup/data/resources to tests, with optional teardown and defined scope.

### Q6. What is `dependency_overrides` in FastAPI?

A mechanism for replacing an application's dependencies during testing so tests can inject controlled implementations. citehttps://fastapi.tiangolo.com/advanced/testing-dependencies/

### Q7. What is `TestClient`?

A convenient client for exercising a FastAPI application in tests without requiring a real network/socket deployment path. citehttps://fastapi.tiangolo.com/reference/testclient/

### Q8. What is a regression test?

A test added or strengthened to prevent a previously discovered bug from returning.

### Q9. What should be mocked?

Usually the dependencies external to the behavior currently being isolated. Avoid mocking the very thing you actually want to verify.

### Q10. What is the difference between unit and integration testing?

Unit tests isolate one component and replace collaborators; integration tests validate interactions with real infrastructure or other components.

---

# 36. Interview Questions — Senior/Staff Level

### Q1. How would you design a test strategy for a large backend?

Start from architectural boundaries. Put most tests at fast, isolated unit levels; maintain integration coverage for persistence and important infrastructure; add API/E2E tests for critical user/system flows.

### Q2. How do you avoid brittle tests?

Test stable contracts rather than implementation details, minimize unnecessary coupling to internal call sequences, isolate state, and mock only where isolation provides real value.

### Q3. How do you test a service that calls three external systems?

Define clear interfaces/dependencies, unit-test business behavior using mocks/fakes, and separately maintain integration/contract tests for the adapters or integrations.

### Q4. Why can too much mocking be dangerous?

Because mocked behavior can diverge from reality. The suite may prove that components interact according to assumptions without proving that the actual dependencies work.

### Q5. How do repositories affect architecture?

They create a persistence boundary. This reduces coupling between business logic and database implementation and provides a controlled seam for testing and replacement.

### Q6. What would you optimize first if a test suite becomes slow?

Measure where the time is spent, then reduce unnecessary integration/E2E setup, improve fixture scope where safe, parallelize appropriately, and move suitable logic to faster unit-level tests.

---

# 37. Cheat Sheet

## pytest

```bash
pytest
pytest -v
pytest tests/unit/
pytest tests/unit/test_student_service.py
```

## Basic test

```python
def test_something():
    assert 1 + 1 == 2
```

## Exception

```python
with pytest.raises(SomeError):
    call()
```

## Fixture

```python
@pytest.fixture
def dependency():
    return ...
```

## Mock

```python
from unittest.mock import Mock

mock = Mock()
mock.method.return_value = value
mock.method.assert_called_once_with(arg)
```

## Mock exception

```python
mock.method.side_effect = RuntimeError("failure")
```

## FastAPI TestClient

```python
from fastapi.testclient import TestClient

client = TestClient(app)
```

## API assertion

```python
response = client.get("/students/1")
assert response.status_code == 200
```

## Dependency override

```python
app.dependency_overrides[original] = replacement
```

## Cleanup

```python
app.dependency_overrides = {}
```

---

# 38. Revision Checklist

Before considering Day 33 fully internalized, you should be able to explain without notes:

- [ ] Why a Repository Pattern exists
- [ ] Why dependency injection improves testability
- [ ] Unit vs integration vs API tests
- [ ] pytest discovery conventions
- [ ] Arrange → Act → Assert
- [ ] pytest fixtures and fixture scopes
- [ ] Purpose of `conftest.py`
- [ ] `Mock`, `MagicMock`, `patch`, `return_value`, `side_effect`
- [ ] How to test service logic without PostgreSQL
- [ ] Why repository tests should use real PostgreSQL
- [ ] How FastAPI `TestClient` works conceptually
- [ ] How FastAPI dependency overrides work
- [ ] Why test failures should be localized by layer
- [ ] Why excessive mocking can make a test suite misleading
- [ ] How regression tests protect against previously fixed bugs

---

# 39. Final Mental Model

The most important concept from Day 33 is not pytest syntax.

It is **designing software so that correctness can be verified cheaply**.

Think:

```text
                   Production System
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
           Router       Service    Repository
             │            │            │
             │            │            ▼
             │            │       PostgreSQL
             │            │
             │            └── mock repository
             │
             └── TestClient / dependency override
```

And remember:

```text
Good architecture
       ↓
Clear boundaries
       ↓
Injectable dependencies
       ↓
Focused tests
       ↓
Fast feedback
       ↓
Safer refactoring
       ↓
More maintainable systems
```

That is the real engineering value of testing.

---

# 40. Day 33 Outcome

Day 33 represents the transition from:

> **“The backend works.”**

to:

> **“The backend has boundaries and automated checks that let engineers change it with confidence.”**

For the Project ₹50L trajectory, this matters because scalable engineering is not only about throughput, SQL, containers, or APIs.

It is also about building systems in which **multiple engineers can safely evolve the codebase over time**.

That is a Principal Engineer mindset: design not merely for today's behavior, but for tomorrow's change.

---

# 41. Exact Learning Resources Used

The Day 33 study session was based on the following official documentation:

### pytest

1. **pytest documentation — Getting Started**  
   https://docs.pytest.org/en/stable/getting-started.html  
   Relevant areas: installing pytest, first test, running tests, assertions, expected exceptions.

2. **pytest documentation — Fixtures**  
   https://docs.pytest.org/en/stable/how-to/fixtures.html  
   Relevant areas: defining fixtures, requesting fixtures, `conftest.py`, fixture reuse and scopes.

### FastAPI

3. **FastAPI — Testing**  
   https://fastapi.tiangolo.com/tutorial/testing/  
   Relevant areas: `TestClient`, test functions, HTTP assertions, separating tests into files/modules.

4. **FastAPI — Testing Dependencies with Overrides**  
   https://fastapi.tiangolo.com/advanced/testing-dependencies/  
   Relevant areas: `app.dependency_overrides`, test-specific dependency replacement, cleanup.

5. **FastAPI — Dependencies**  
   https://fastapi.tiangolo.com/tutorial/dependencies/  
   Relevant areas: dependency injection model and why dependencies are useful for shared resources and cross-cutting behavior.

### Python standard library

6. **Python — `unittest.mock`**  
   https://docs.python.org/3/library/unittest.mock.html  
   Relevant areas: `Mock`, `MagicMock`, `patch`, `return_value`, `side_effect`, call assertions, patching in the correct namespace.

---

# 42. One-Page Memory Card

```text
REPOSITORY
──────────
Data-access boundary.

SERVICE
───────
Business logic.

ROUTER
──────
HTTP/API boundary.

DI
──
Inject dependencies instead of constructing them internally.

UNIT TEST
─────────
Test one component in isolation.

MOCK
────
Replace a collaborator and verify behavior/interactions.

INTEGRATION TEST
────────────────
Verify real component interaction, especially with PostgreSQL.

API TEST
────────
Exercise HTTP behavior using FastAPI TestClient.

FIXTURE
───────
Reusable test setup/resource.

CONFTTEST.PY
────────────
Shared pytest fixtures/configuration location.

DEPENDENCY OVERRIDE
───────────────────
Replace FastAPI dependencies for controlled tests.

KEY PRINCIPLE
─────────────
Test each responsibility at the boundary where that responsibility lives.
```

---

## End of Day 033 Handbook

**Project ₹50L — From Senior Software Engineer → AI Platform & Systems Principal Engineer**
