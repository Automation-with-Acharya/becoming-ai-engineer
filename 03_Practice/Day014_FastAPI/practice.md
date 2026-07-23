## Exercise 1: Create `StudentCreate`

### Fields

- `name`
- `age`
- `city`
- `email`

Add validations.

## Exercise 2: Create `StudentResponse`

Hide any internal fields that clients should not receive.

## Exercise 3: Add `Field()`

### Example

```python
name: str = Field(
    min_length=2,
    max_length=50,
    description="Student Name"
)
```

## Exercise 4: Add Validations

Add the following validations:

- `age > 0`
- Minimum length for `name`
- Minimum length for `city`
- Email validation (use `EmailStr` if available)

## Exercise 5: Update FastAPI Routes

Use:

```python
response_model=StudentResponse
```

Instead of returning raw dictionaries.

## Exercise 6: Open Swagger

Verify the following:

- Validation errors
- Required fields
- Generated documentation
- Examples

Observe how Swagger automatically updates.
