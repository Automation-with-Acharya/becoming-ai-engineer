# Day 016: Middleware Practice

## Exercise 1: Log Incoming Requests

Create middleware that prints the incoming request method and path.

Example output:

```text
Incoming Request:
GET /students
```

## Exercise 2: Measure Execution Time

Measure how long each request takes to complete.

Example output:

```text
Request completed in 18 ms
```

Add the execution time as a custom response header.

## Exercise 3: Add Console Logging

Add simple console logging for each completed request.

Example output:

```text
GET /students -> 200 OK
```

## Exercise 4: Enable CORS

Enable CORS for the application.

Allowed origin:

```text
http://localhost:5173
```

Verify that your application still works after enabling CORS.

## Exercise 5: Experiment With Middleware Order

Create two middleware functions.

Observe:

- Execution order
- Response order

This is a great way to understand the middleware pipeline.
