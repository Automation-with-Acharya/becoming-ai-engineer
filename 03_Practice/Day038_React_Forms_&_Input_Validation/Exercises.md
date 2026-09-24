# React Forms and Input Validation Exercises

## Exercise 1: Build `AddStudentForm`

Create the following structure:

```text
src/
├── components/
│   ├── AddStudentForm.jsx
│   ├── StudentCard.jsx
│   ├── StudentList.jsx
│   └── ...
```

The form should contain:

- Name
- Age
- City
- Email
- Active
- Submit

## Exercise 2: Controlled Fields

Create one form state object:

```jsx
const [form, setForm] = useState({
  name: "",
  age: "",
  city: "",
  email: "",
  is_active: true,
});
```

Connect the input value to the corresponding form field:

```text
input value
    ↓
form.field
```

Connect input changes to the state update:

```text
input change
    ↓
handleChange
    ↓
setForm(...)
```

At the end of this exercise, every visible field must be controlled by React.

## Exercise 3: Generic Change Handler

Implement:

```jsx
function handleChange(event) {
  const { name, value, type, checked } = event.target;

  setForm((previous) => ({
    ...previous,
    [name]: type === "checkbox" ? checked : value,
  }));
}
```

This gives you one handler for:

- Text input
- Number input
- Email input
- Checkbox

> **Important:** For checkboxes, read `event.target.checked`, not `event.target.value`.

React's current `<input>` documentation explicitly distinguishes `value` for text-like inputs from `checked` for controlled checkboxes.

## Exercise 4: Native HTML Validation

Start with browser-supported validation.

For example:

```jsx
<input
  name="name"
  value={form.name}
  onChange={handleChange}
  required
  minLength={2}
  maxLength={100}
/>
```

**Age:**

```jsx
<input
  type="number"
  name="age"
  value={form.age}
  onChange={handleChange}
  required
  min={0}
/>
```

**Email:**

```jsx
<input
  type="email"
  name="email"
  value={form.email}
  onChange={handleChange}
  required
/>
```

**City:**

```jsx
<input
  name="city"
  value={form.city}
  onChange={handleChange}
  required
  minLength={1}
  maxLength={100}
/>
```

This lets the browser reject clearly invalid input before your custom logic runs. HTML's constraint-validation system supports these kinds of constraints.

## Exercise 5: React-Level Validation

Add a small validation layer for business-friendly messages.

Example:

```jsx
function validateForm(form) {
  const errors = {};

  if (!form.name.trim()) {
    errors.name = "Name is required.";
  }

  if (!form.city.trim()) {
    errors.city = "City is required.";
  }

  if (!form.email.trim()) {
    errors.email = "Email is required.";
  }

  return errors;
}
```

Then define the error state:

```jsx
const [errors, setErrors] = useState({});
```

Validate before submitting:

```jsx
const validationErrors = validateForm(form);

if (Object.keys(validationErrors).length > 0) {
  setErrors(validationErrors);
  return;
}
```

Don't attempt to duplicate every Pydantic rule.

The purpose is:

```text
Client
    ↓
Fast feedback
```

while:

```text
Server
    ↓
Authoritative validation
```

## Exercise 6: Error Display

Display field-specific errors:

```jsx
{
  errors.name && <p className="field-error">{errors.name}</p>;
}
```

Accessibility improvement:

```jsx
<input aria-invalid={Boolean(errors.name)} aria-describedby="name-error" />;

{
  errors.name && <p id="name-error">{errors.name}</p>;
}
```

Don't spend the session building a giant accessibility framework.

Understand the principle: the UI should make invalid state understandable to both the user and assistive technology.

## Exercise 7: Submit to FastAPI

Extend `src/api/studentApi.js` with:

```js
export async function createStudent(student) {
  const response = await fetch("/api/students/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(student),
  });

  if (!response.ok) {
    throw new Error(`Failed to create student: HTTP ${response.status}`);
  }

  return response.json();
}
```

Your architecture becomes:

```text
AddStudentForm
    ↓
createStudent()
    ↓
POST /api/students/
    ↓
Vite proxy
    ↓
FastAPI
    ↓
Pydantic
    ↓
Service
    ↓
Repository
    ↓
PostgreSQL
```

This is the full-stack write path.

## Exercise 8: Add Submitting State

Introduce:

```jsx
const [submitting, setSubmitting] = useState(false);
```

Then:

```jsx
try {
  setSubmitting(true);

  await createStudent(payload);
} finally {
  setSubmitting(false);
}
```

And:

```jsx
<button type="submit" disabled={submitting}>
  {submitting ? "Creating..." : "Add Student"}
</button>
```

Now the form explicitly understands:

```text
Idle
    ↓
Submitting
    ↓
Success / Error
```

## Exercise 9: Handle API Errors

Your backend can reject the request.

Examples:

- `400 Bad Request`
- `422 Validation Error`
- `409 Conflict`
- `500 Internal Server Error`

Today's frontend should at least distinguish:

```text
Client validation failure
          vs
Server/API failure
```

For the API failure:

```jsx
const [submitError, setSubmitError] = useState(null);
```

Then:

```jsx
try {
  await createStudent(payload);
} catch (error) {
  setSubmitError(error.message);
}
```

Display:

```jsx
{
  submitError && <p role="alert">{submitError}</p>;
}
```

## Exercise 10: Refresh the Student List

After a successful creation:

```text
POST /students
    ↓
201 Created
    ↓
New Student
    ↓
UI needs latest list
```

For today's architecture, use the simplest correct approach:

```text
createStudent()
    ↓
success
    ↓
reload students
```

Conceptually:

```jsx
await createStudent(payload);
await reloadStudents();
```

This gives you the first complete write-read cycle:

```text
GET students
    ↓
Display

POST student
    ↓
Database
    ↓
GET students
    ↓
Display updated list
```

Do not introduce React Query or a global state library today. We need to understand the fundamental flow first.

## Exercise 11: Reset the Form

After successful creation:

```jsx
setForm({
  name: "",
  age: "",
  city: "",
  email: "",
  is_active: true,
});

setErrors({});
```

The user should return to a clean form.

This introduces another useful React state transition:

```text
SUCCESS
    ↓
Reset Form
    ↓
EMPTY
```

## Exercise 12: Build the First CRUD Write Flow

At the end of today, you should have:

```text
┌─────────────────────────────────────────────┐
│ Student Management                          │
│                                             │
│ Add Student                                 │
│                                             │
│ Name: [____________________]                │
│ Age: [____]                                 │
│ City: [____________________]                │
│ Email: [____________________]               │
│ Active [✓]                                  │
│                                             │
│ [ Add Student ]                             │
│                                             │
│ Students                                    │
│ ┌─────────────────────────────────────────┐ │
│ │ Existing Student                        │ │
│ └─────────────────────────────────────────┘ │
│                                             │
└─────────────────────────────────────────────┘
```

The important point isn't visual polish.

It's this:

```text
FORM
    ↓
REACT STATE
    ↓
VALIDATION
    ↓
HTTP POST
    ↓
FASTAPI
    ↓
POSTGRESQL
    ↓
REFRESH
    ↓
UI
```

## Exercise 13: Deliberately Break the Form

This is important.

Try:

- Empty name
- Invalid email
- Negative age
- Empty city

Observe browser validation.

Then deliberately bypass it or modify the request if practical and send bad JSON to FastAPI.

Observe server validation.

This experiment should make the distinction permanent:

```text
Frontend validation
        ≠
Backend validation
```
