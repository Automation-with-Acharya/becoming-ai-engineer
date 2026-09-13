# Day 35 — Backend Test Strategy

## Exercise 1 — Run the Entire Suite

Start with:

```bash
pytest -v
```

Capture the following metrics:

- Total tests
- Passed
- Failed
- Skipped
- Execution time

At the current baseline, you have already reached:

- 11 unit tests
- 17 integration tests
- 11 API tests
- 39 total tests

This is from Day 34.

The goal for today is to make the suite more useful, not just larger.

---

## Exercise 2 — Introduce Test Markers

Add markers such as:

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.api
```

Then run:

```bash
pytest -m unit -v
pytest -m integration -v
pytest -m api -v
```

You should now have a structure like this:

```text
                    ALL TESTS
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
       unit        integration          api
```

This is the beginning of a real test execution strategy.

---

## Exercise 3 — Parametrize Validation Tests

Look for tests that are essentially the same rule with different invalid inputs.

Example invalid cases:

```python
age = -1
age = 0
age = 151
```

If your validation rules support those cases, convert them into one parametrized test.

Conceptually:

```python
@pytest.mark.parametrize(
    "age",
    [-1, 0, 151]
)
def test_invalid_age(age):
    ...
```

The goal is not to reduce line count.

The goal is to express:

> One behavior, many examples.

---

## Exercise 4 — Generate a Coverage Report

Run:

```bash
coverage run -m pytest
```

Then:

```bash
coverage report
```

And:

```bash
coverage html
```

Open the generated HTML report.

Now identify:

- Which files have high coverage?
- Which files have low coverage?
- Which important branches are not exercised?

This is the first time you are viewing the test suite as a system rather than as isolated tests.

---

## Exercise 5 — Identify the Most Important Untested Code

Do not immediately add tests for every uncovered line.

Instead, classify uncovered code by priority:

- Category A: Important business logic → HIGH PRIORITY
- Category B: Error handling → HIGH PRIORITY
- Category C: Rare infrastructure branch → MEDIUM
- Category D: Defensive / unreachable code → LOW

This teaches an important engineering lesson:

> Coverage improvement should be risk-driven, not percentage-driven.

---

## Exercise 6 — Add One High-Value Regression Test

Look for bugs encountered throughout the project, such as:

- Missing student
- DB constraint failure
- Incorrect DB_HOST
- Startup race condition
- Transaction rollback
- Dependency override problem

Pick one realistic regression scenario and create a permanent automated test for it.

Your test should answer this question:

> If someone accidentally reintroduces this bug six months from now, will pytest catch it?

That is a high-value test.

---

## Exercise 7 — Create a Smoke Test Group

Identify a few critical paths:

- Health
- Login
- Get Student
- Create Student

Mark those as:

```python
@pytest.mark.smoke
```

Then run:

```bash
pytest -m smoke
```

This gives you the beginnings of a CI/CD concept:

```text
New Build
    ↓
Smoke Tests
    ↓
Pass?
 ┌────┴────┐
 │        │
No       Yes
 │        │
Stop    Continue
    ↓
Full Test Suite
```

This is how testing begins to become part of deployment engineering.

---

## Exercise 8 — Test the Complete Critical Path

Select one important user journey and trace it through the system:

```text
HTTP request
    ↓
Router
    ↓
Dependency
    ↓
Service
    ↓
Repository
    ↓
PostgreSQL
    ↓
Response
```

Then identify which test layer protects each part.

Example mapping:

- Router → API test
- Service → Unit test
- Repository → Integration test
- PostgreSQL → Integration test

This gives you a coverage map of responsibilities.

---

## Exercise 9 — Repository Quality Review

Open:

```text
repositories/student_repository.py
```

Ask:

- Are method names business-oriented?
- Are SQL details isolated?
- Are transactions handled consistently?
- Are errors propagated appropriately?
- Are return models clear?

Then inspect:

```text
services/student_service.py
```

Ask:

- Is business logic still outside the repository?
- Is database knowledge leaking upward?
- Could the service be tested without PostgreSQL?

This is a miniature architecture review.

---

## Exercise 10 — Final Test Architecture Diagram

Document the architecture like this:

```text
                         Student Backend

                             Router
                               │
                               │
                        ┌──────▼──────┐
                        │  API Tests  │
                        │  TestClient │
                        └──────┬──────┘
                               │
                               ▼
                           Service
                               │
                        ┌──────▼──────┐
                        │ Unit Tests  │
                        │ Mock Repo   │
                        └─────────────┘

                           Repository
                               │
                        ┌──────▼──────────┐
                        │ Integration     │
                        │ Tests           │
                        └──────┬──────────┘
                               │
                               ▼
                          PostgreSQL
```

Then add the testing lifecycle:

```text
Coverage
   ↓
Regression Tests
   ↓
Smoke Tests
   ↓
CI/CD
```

This is your Day 35 architecture artifact.

---

## Summary

By the end of this exercise set, you are shifting from:

- writing tests individually

to:

- designing a testing strategy for the entire backend system.

This is the foundation for reliable engineering, better deployment confidence, and sustainable software quality.
