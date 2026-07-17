# Pydantic and Request Models

## 1. What is Pydantic?

Pydantic is a widely used Python library for data validation and settings management.

At its core, it enforces type hints at runtime and provides clear error messages when data is invalid. Instead of assuming that incoming data is in the right format, Pydantic ensures that it matches the structure you define.

### How it works

You define the structure of your data by creating a class that inherits from Pydantic's `BaseModel`:

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool = True
```

If you pass a dictionary like this:

```python
{"id": "123", "name": "Alice", "email": "alice@example.com"}
```

Pydantic will:

- Validate the data and ensure required fields are present.
- Coerce types automatically, such as converting the string `"123"` into the integer `123`.
- Fail safely by raising a structured error if the data is invalid.

---

## 2. Why do we use request models?

Request models are Pydantic models used to define the exact shape of incoming payload data, such as a JSON body in a POST request.

We use them for several important reasons:

### Automatic validation and type safety

Without request models, you would need to manually check incoming data, which is repetitive and error-prone.

```python
# Manual validation approach
if "username" not in request.json:
    return "Missing username", 400
if not isinstance(request.json["age"], int):
    return "Age must be an integer", 400
```

With a Pydantic request model, the framework handles this automatically. If the client sends invalid data, the server rejects it with a clear `422 Unprocessable Entity` response before your core logic runs.

### Parsing instead of just validating

Pydantic does more than validate; it parses raw input into native Python types. For example, a date provided as a string can be converted into a Python `date` object.

### Auto-generated API documentation

Frameworks like FastAPI use request models to generate interactive API documentation such as Swagger UI or ReDoc.

This helps frontend developers and API consumers understand exactly what schema the request should follow.

### Better editor support

Once data is parsed into a request model, your IDE can provide better autocomplete, type checking, and linting, reducing bugs and typos in your application logic.
