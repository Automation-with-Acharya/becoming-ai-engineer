# Day 017: Python Logging Practice

## Exercise 1: Configure Logging

Configure logging:

```python
logging.basicConfig(...)
```

Write logs to the console.

## Exercise 2: Write Logs to a File

Write logs to:

```text
logs/application.log
```

## Exercise 3: Replace Print Statements

Replace existing `print()` statements in your project with:

```python
logger.info()
logger.error()
logger.warning()
```

## Exercise 4: Log Exceptions

Inside a `try`/`except` block:

- Log the exception.

Example:

```python
logger.exception("Failed to create student")
```

Observe how the stack trace is recorded.

## Exercise 5: Review Logging Output

Trigger an intentional error.

Review:

- Console output
- Log file
- Stack trace

Compare both.
