# Day 035 — Backend Test Strategy, Coverage & Reliability

**Project:** Project ₹50L — AI Platform & Systems Principal Engineer Roadmap  
**Date:** Wednesday, 9 September 2026  
**Phase:** Phase 1 — Backend & Engineering Foundations  
**Week:** Week 5 — Advanced SQL, Database Optimization, Repository Improvements & Testing  
**Session:** Backend Reliability Checkpoint  
**Estimated Session:** ~2 hours

---

## 1. Learning Objectives

By the end of this session, the goal is to be able to:

1. Organize tests into meaningful categories rather than treating the test suite as one undifferentiated collection.
2. Use `pytest` markers to select logical test groups.
3. Use parametrization to avoid repetitive test code while increasing input coverage.
4. Measure code coverage with `coverage.py`.
5. Understand why high coverage does **not** automatically mean high correctness.
6. Think in terms of regression protection and critical-path testing.
7. Build a small smoke-test layer for fast confidence.
8. Identify high-risk code that deserves additional tests.
9. Review repository quality from the perspective of future maintainability and CI reliability.
10. Connect unit, integration, API, regression, smoke, and coverage practices into one backend testing strategy.

---

# 2. Big Picture

The previous days established the technical testing foundation:

- **Day 033:** automated testing with unit and API tests.
- **Day 034:** database integration testing, constraints, transaction rollback, atomicity, cleanup, and suite isolation.
- **Day 035:** step back and answer the larger engineering question:

> **How do we turn a collection of passing tests into a reliable backend test strategy?**

A mature backend does not merely ask:

> “Do all tests pass?”

It also asks:

> “What behavior is protected?”
>
> “At what layer is that behavior tested?”
>
> “How quickly can I detect a critical regression?”
>
> “What important code is still untested?”
>
> “Can I run the right subset of tests during development and CI?”

This is the purpose of test strategy.

---

# 3. Test Strategy Mental Model

A useful model for the backend is:

```text
                         BACKEND RELIABILITY
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
          Correctness          Speed              Regression
             │                    │                    │
       ┌─────┼─────┐        ┌─────┼─────┐        ┌─────┼─────┐
       │     │     │        │     │     │        │     │     │
     Unit   Int.  API      Smoke  Subset Full    Critical Edge
       │     │     │        │     │     │        │     │     │
       └─────┴─────┴────────┴─────┴─────┴────────┴─────┴─────┘
                              │
                         Test Strategy
                              │
                      Coverage + Risk Review
```

The important idea is that different test types answer different questions.

| Test layer            | Primary question                                               |                Typical speed |
| --------------------- | -------------------------------------------------------------- | ---------------------------: |
| Unit                  | Does this isolated piece of logic behave correctly?            |                    Very fast |
| Integration           | Does this component interact correctly with a real dependency? |                       Medium |
| API                   | Does the externally visible endpoint behavior work?            |                       Medium |
| Smoke                 | Does the critical path work at all?                            |                         Fast |
| Full regression suite | Did the broader behavior remain intact?                        |                      Slowest |
| Coverage              | Which code paths are exercised?                                | Measurement, not correctness |

The goal is **not** to maximize one metric. The goal is to create confidence efficiently.

---

# 4. Pytest Markers

## 4.1 Why markers exist

As a project grows, running every test for every small change becomes increasingly expensive.

Markers let us classify tests so we can intentionally run subsets.

For example:

```python
import pytest


@pytest.mark.unit
def test_password_validation():
    ...


@pytest.mark.integration
def test_student_repository_insert():
    ...


@pytest.mark.api
def test_create_student_endpoint():
    ...
```

Now the suite can be queried by category.

---

## 4.2 Running a marked subset

Examples:

```bash
pytest -m unit
```

```bash
pytest -m integration
```

```bash
pytest -m api
```

A useful combined selection can also be expressed with marker expressions:

```bash
pytest -m "unit or api"
```

The exact marker names should reflect the repository's actual test architecture rather than becoming an arbitrary collection of labels.

---

## 4.3 Registering custom markers

Custom markers should be registered in pytest configuration so the test suite documents its supported categories.

Example:

```ini
[pytest]
markers =
    unit: fast isolated tests
    integration: tests requiring real external components
    api: API endpoint tests
    smoke: critical path tests
```

This improves discoverability and avoids unknown-marker warnings.

---

# 5. Parametrization

## 5.1 Problem: repetitive tests

Suppose several inputs should all produce the same validation result.

Without parametrization, the suite can become repetitive:

```python
def test_invalid_email_1():
    ...


def test_invalid_email_2():
    ...


def test_invalid_email_3():
    ...
```

This can usually be expressed more clearly with `pytest.mark.parametrize`.

---

## 5.2 Basic pattern

```python
import pytest


@pytest.mark.parametrize(
    "email",
    [
        "",
        "not-an-email",
        "missing-at-symbol.com",
    ],
)
def test_invalid_email(email):
    assert is_valid_email(email) is False
```

The same behavioral rule is exercised across multiple inputs.

---

## 5.3 Multiple parameters

```python
@pytest.mark.parametrize(
    "age, expected",
    [
        (0, False),
        (17, False),
        (18, True),
        (65, True),
    ],
)
def test_age_validation(age, expected):
    assert is_valid_age(age) is expected
```

This is especially useful for:

- boundary conditions,
- validation rules,
- equivalent input classes,
- known regression cases,
- combinations of input and expected result.

---

# 6. Coverage with `coverage.py`

## 6.1 What coverage measures

Coverage tooling answers a narrow but important question:

> **Which executable code was exercised while the tests ran?**

Typical commands:

```bash
coverage run -m pytest
```

Then:

```bash
coverage report
```

For a browsable report:

```bash
coverage html
```

The HTML report can then be inspected for files and lines that were not exercised.

---

## 6.2 Coverage is not correctness

This distinction is critical.

Consider:

```python
def calculate_discount(total):
    if total >= 1000:
        return 0.20
    return 0.05
```

A single test such as:

```python
def test_discount():
    assert calculate_discount(1200) == 0.20
```

executes the function, so coverage increases.

But the lower branch is still untested.

Therefore:

```text
Coverage = code was executed

Correctness = behavior was verified
```

These are related, but they are not the same thing.

---

# 7. Coverage and Risk

Coverage becomes much more valuable when combined with engineering judgment.

A line of code can be:

- highly covered and low risk,
- poorly covered and low risk,
- highly covered but incorrectly tested,
- poorly covered and business-critical.

The last category should receive immediate attention.

A better review question is:

> **Which important behaviors lack meaningful protection?**

rather than:

> **How do I make the percentage bigger?**

---

# 8. Test Pyramid Mental Model

For most backend systems, the test suite should contain many fast tests and fewer expensive tests.

```text
                    /\
                   /  \
                  / API \
                 /------\
                /        \
               /Integration\
              /------------\
             /              \
            /     Unit       \
           /------------------\
```

Conceptually:

```text
              fewer / slower
                    ▲
                    │
                 API tests
                    │
             Integration tests
                    │
                  Unit tests
                    │
              more / faster
```

The exact distribution depends on the application, but the principle is stable:

> Put fast feedback close to the logic and use higher-level tests to protect system integration and externally visible behavior.

---

# 9. Unit vs Integration vs API

The repository can think about responsibilities like this:

```text
┌──────────────────────────────────────────┐
│ API tests                                │
│ Endpoint contract + request/response     │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Integration tests                        │
│ Repository + PostgreSQL + transactions   │
└────────────────────┬─────────────────────┘
                     │
┌────────────────────▼─────────────────────┐
│ Unit tests                               │
│ Isolated business / helper logic         │
└──────────────────────────────────────────┘
```

Examples:

| Behavior                               | Good test layer      |
| -------------------------------------- | -------------------- |
| Pure validation function               | Unit                 |
| Repository SQL against real PostgreSQL | Integration          |
| UNIQUE constraint behavior             | Integration          |
| Transaction atomicity                  | Integration          |
| HTTP status code                       | API                  |
| Request validation through FastAPI     | API                  |
| End-to-end critical operation          | Smoke / higher-level |

No single layer should be forced to prove everything.

---

# 10. Regression Thinking

A regression is a previously working behavior that becomes broken after a change.

The best regression test has three properties:

1. It captures behavior that matters.
2. It would fail if the underlying defect returned.
3. It is easy enough to keep permanently.

Example:

```text
Bug discovered
      │
      ▼
Understand expected behavior
      │
      ▼
Add focused regression test
      │
      ▼
Fix defect
      │
      ▼
Keep test forever
```

This converts an old defect into a permanent safety mechanism.

---

# 11. Smoke Tests

Smoke tests provide a fast signal for a critical path.

Example:

```python
import pytest


@pytest.mark.smoke
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
```

A real project can choose a small collection of truly essential checks, such as:

- service starts,
- health endpoint responds,
- critical authentication path works,
- critical create/read workflow works.

The important property is that the smoke suite stays small and meaningful.

Run it with:

```bash
pytest -m smoke
```

Smoke tests are not a replacement for the full suite.

They are a fast confidence layer.

---

# 12. The Reliability Feedback Loop

A practical development loop is:

```text
           Change code
               │
               ▼
        Run targeted tests
               │
               ▼
         Run smoke tests
               │
               ▼
        Run broader suite
               │
               ▼
      Measure coverage/risk
               │
               ▼
   Add missing regression protection
               │
               └───────────────► next change
```

This creates a feedback system rather than treating testing as a final activity.

---

# 13. Critical-Path Mapping

A useful exercise is to map important backend workflows to their protective tests.

Example:

| Critical behavior          | Unit | Integration | API | Smoke |
| -------------------------- | :--: | :---------: | :-: | :---: |
| Input validation           |  ✓   |             |  ✓  |       |
| Repository insert          |      |      ✓      |     |       |
| Database constraints       |      |      ✓      |     |       |
| Transaction atomicity      |      |      ✓      |     |       |
| Endpoint response contract |      |             |  ✓  |       |
| Service health             |      |             |  ✓  |   ✓   |

This table exposes gaps much faster than a raw coverage number.

---

# 14. Repository Quality Review

A test suite is part of the repository architecture.

A quality review should check:

### Test discoverability

Can a new engineer quickly find:

- unit tests,
- integration tests,
- API tests,
- fixtures,
- test configuration?

### Test isolation

Does one test depend accidentally on another?

### Determinism

Does the same test produce the same result repeatedly?

### Naming

Can the test name explain the behavior or failure scenario?

### Fast feedback

Can developers run only the relevant layer or marker?

### Critical-path protection

Are high-value workflows actually protected?

### CI readiness

Can the same test commands run reliably in a clean environment?

---

# 15. Common Mistakes

## Mistake 1 — Chasing coverage percentage

A high number can still hide weak assertions.

**Better:** prioritize important behavior.

## Mistake 2 — Making every test an integration test

This increases runtime and makes failures harder to localize.

**Better:** isolate pure logic where possible.

## Mistake 3 — Too many end-to-end/smoke checks

The smoke suite should remain quick.

**Better:** reserve it for critical paths.

## Mistake 4 — Repeating nearly identical tests

This creates maintenance overhead.

**Better:** use parametrization for input families.

## Mistake 5 — Ignoring untested branches

A function can have high overall execution coverage while important edge cases remain unverified.

**Better:** inspect uncovered branches in business-critical code.

## Mistake 6 — Treating passing tests as proof of production readiness

A passing suite only proves the behavior that the suite actually checks.

**Better:** combine tests, coverage, architecture review, and risk analysis.

---

# 16. Enterprise Mapping — ASP.NET Core

The same strategy maps naturally to the .NET ecosystem.

| Python / pytest concept | ASP.NET Core / .NET equivalent                             |
| ----------------------- | ---------------------------------------------------------- |
| `pytest`                | xUnit / NUnit / MSTest                                     |
| pytest marker           | Trait / category                                           |
| `parametrize`           | `[Theory]` + `[InlineData]` / `[MemberData]`               |
| unit test               | xUnit unit test                                            |
| integration test        | `WebApplicationFactory<TEntryPoint>` / integration harness |
| API test                | `HttpClient` against test server                           |
| coverage.py             | Coverlet / `dotnet test` coverage tooling                  |
| smoke test              | Tagged/traited critical-path test suite                    |

Example xUnit parametrization:

```csharp
[Theory]
[InlineData(17, false)]
[InlineData(18, true)]
[InlineData(65, true)]
public void ValidateAge_ReturnsExpectedResult(int age, bool expected)
{
    var result = ValidateAge(age);

    Assert.Equal(expected, result);
}
```

The syntax changes.

The engineering principles do not.

---

# 17. CI/CD Mental Model

A mature CI pipeline can use the test layers progressively:

```text
Pull Request
     │
     ▼
Fast unit tests
     │
     ▼
Smoke / selected API tests
     │
     ▼
Integration tests
     │
     ▼
Full regression suite
     │
     ▼
Coverage / quality checks
     │
     ▼
Deployment confidence
```

The exact pipeline can vary by repository, but the core principle is:

> **Fast failures should happen as early as possible.**

This is one reason test categorization and markers become valuable as repositories grow.

---

# 18. Engineering Mental Models

## Mental Model 1 — Coverage is a map, not a score

Coverage shows where tests traveled.

It does not tell you whether the destination was correct.

---

## Mental Model 2 — Tests are executable contracts

A strong test describes behavior the system must continue to preserve.

---

## Mental Model 3 — Risk determines test investment

Not every line deserves equal testing effort.

Business-critical, security-sensitive, transaction-heavy, and failure-prone paths deserve stronger protection.

---

## Mental Model 4 — Test at the cheapest layer that proves the behavior

```text
Can a unit test prove it?
        │
       Yes ──► use unit test
        │
       No
        ▼
Can integration prove it?
        │
       Yes ──► use integration test
        │
       No
        ▼
Use higher-level/API/end-to-end coverage
```

This reduces unnecessary test cost.

---

## Mental Model 5 — Every production bug can become a permanent test

A defect should ideally leave behind a regression test so the exact failure mode becomes harder to reintroduce.

---

# 19. Day 035 Hands-On Exercise Structure

The session's practical work was organized around the following sequence.

### Exercise 1 — Baseline

Run the full test suite:

```bash
pytest -v
```

Record the result and runtime.

### Exercise 2 — Test markers

Categorize tests into logical groups such as:

```text
unit
integration
api
smoke
```

Then run each group independently.

### Exercise 3 — Parametrization

Convert a repetitive validation test family into a parametrized test.

### Exercise 4 — Coverage

Run:

```bash
coverage run -m pytest
coverage report
coverage html
```

Inspect uncovered code paths.

### Exercise 5 — Risk review

Identify code that is both:

- important,
- insufficiently protected.

### Exercise 6 — Regression test

Add one focused test for a meaningful behavior or previously vulnerable path.

### Exercise 7 — Smoke suite

Create a small critical-path marker and verify:

```bash
pytest -m smoke
```

### Exercise 8 — Critical-path map

Map important backend workflows to the test layer that protects them.

### Exercise 9 — Repository quality review

Check naming, structure, isolation, discoverability, and repeatability.

### Exercise 10 — Architecture diagram

Document how unit, integration, API, smoke, coverage, and regression practices work together.

---

# 20. Example Repository Test Structure

A scalable structure might look like:

```text
tests/
├── unit/
│   ├── test_validation.py
│   └── test_helpers.py
│
├── integration/
│   ├── test_student_repository.py
│   ├── test_transactions.py
│   └── test_constraints.py
│
├── api/
│   ├── test_students_api.py
│   └── test_health_api.py
│
├── smoke/
│   └── test_critical_paths.py
│
└── conftest.py
```

The exact repository structure may differ. The architectural purpose is what matters: tests should be easy to locate and reason about.

---

# 21. Interview Questions

## Q1. Is 100% test coverage the goal?

Not by itself.

Coverage measures exercised code, not correctness. High-risk behaviors and meaningful assertions matter more than maximizing a percentage mechanically.

---

## Q2. Why use pytest markers?

They allow logical test grouping and selective execution, which improves developer feedback speed and makes CI stages easier to organize.

---

## Q3. When should you use parametrization?

When the same behavioral rule should be validated against multiple inputs, especially boundary values, invalid values, or known regression cases.

---

## Q4. What is a smoke test?

A small, fast set of checks that verifies the application's most critical functionality is alive and usable.

---

## Q5. Why not test everything through the API?

API tests provide useful system-level confidence, but they are slower and make failures less localized. Lower-level unit and integration tests can provide faster, more precise feedback for many behaviors.

---

## Q6. What should happen after discovering a production bug?

Reproduce it, add a regression test that fails for the defect, fix the issue, and retain the test as permanent protection.

---

## Q7. How does coverage help an engineer?

It highlights code paths that were not exercised by the current test suite, giving the engineer a map for further risk analysis and test improvement.

---

## Q8. What makes a test valuable?

A valuable test protects meaningful behavior, has clear assertions, is deterministic, is maintainable, and would fail when an important regression occurs.

---

# 22. Cheat Sheet

```text
PYTEST MARKERS
--------------
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.api
@pytest.mark.smoke

RUN SUBSETS
-----------
pytest -m unit
pytest -m integration
pytest -m api
pytest -m smoke

PARAMETRIZATION
---------------
@pytest.mark.parametrize("input,expected", [...])

COVERAGE
--------
coverage run -m pytest
coverage report
coverage html

CORE PRINCIPLES
---------------
Coverage != correctness
Test behavior, not implementation details
Test at the cheapest layer that proves the behavior
Keep smoke tests small and meaningful
Use regression tests to preserve bug fixes
Use risk to guide test investment
```

---

# 23. Final Mental Model

The test suite is not simply a pile of green checks.

It is an engineering safety system:

```text
             CODE CHANGE
                  │
                  ▼
          ┌───────────────┐
          │ Targeted Tests│
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │ Smoke Tests   │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │ Full Suite    │
          └───────┬───────┘
                  │
                  ▼
          ┌───────────────┐
          │ Coverage Map  │
          └───────┬───────┘
                  │
                  ▼
        Identify risk / gaps
                  │
                  ▼
        Add regression protection
                  │
                  └──────────► SAFER NEXT CHANGE
```

The goal is not:

> **“Make the test percentage as high as possible.”**

The goal is:

> **“Make important system behavior difficult to break without detection.”**

That is the engineering mindset behind a reliable backend.

---

# 24. Revision Checklist

Before considering Day 035 fully revised, confirm that you can explain:

- [ ] What pytest markers are and why they matter.
- [ ] How to run tests by marker.
- [ ] Why custom markers should be registered.
- [ ] When parametrization is useful.
- [ ] How to run `coverage.py`.
- [ ] Why coverage is not equivalent to correctness.
- [ ] How to identify high-risk uncovered behavior.
- [ ] The difference between unit, integration, API, smoke, and regression tests.
- [ ] Why smoke tests should remain small.
- [ ] How a production bug becomes a regression test.
- [ ] How test strategy maps to ASP.NET Core/.NET.
- [ ] Why fast feedback matters in CI/CD.

---

# 25. Official Resources

### pytest — Marks

https://docs.pytest.org/en/stable/how-to/mark.html

### pytest — Parametrization

https://docs.pytest.org/en/stable/how-to/parametrize.html

### pytest — Good Integration Practices

https://docs.pytest.org/en/stable/explanation/goodpractices.html

### coverage.py Documentation

https://coverage.readthedocs.io/en/latest/

---

# 26. Completion Criteria

Day 035 is complete when the engineer can:

1. Run the complete backend test suite with confidence.
2. Select relevant test subsets using markers.
3. Reduce repetitive tests with parametrization.
4. Generate and interpret a coverage report.
5. Distinguish code coverage from behavioral correctness.
6. Identify important gaps using risk rather than percentage alone.
7. Protect a critical workflow with a smoke test.
8. Add a meaningful regression test.
9. Explain the repository's test architecture clearly.
10. Translate the same testing principles into a .NET / ASP.NET Core environment.

---

## One-Line Takeaway

> **Measure coverage → identify important behavior → test at the right layer → protect regressions → keep a fast smoke path → make future changes safer.**
