# Day 037: React and FastAPI Integration Exercises

These exercises connect the React frontend to the FastAPI backend and practice the complete browser-to-API workflow.

## Exercise 1: Verify the FastAPI Backend

Start the backend using the existing project setup.

Confirm that the Student Router exposes the expected endpoint:

```http
GET /students
```

The exact route may differ in the current project. Open Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) and verify that the endpoint works before changing React.

This creates the following baseline:

- [x] The backend works independently.

## Exercise 2: Identify the API Contract

Before writing `fetch()`, inspect the real response returned by the backend.

Example response:

```json
[
  {
    "id": 1,
    "name": "Mayank Acharya",
    "age": 28,
    "city": "Gandhinagar",
    "email": "mayank@example.com",
    "active": true
  }
]
```

The React component should consume the actual API contract. Do not invent a second frontend data format unless there is a deliberate reason to do so.

## Exercise 3: Create an API Module

Do not put HTTP requests directly inside `StudentCard.jsx`. Create a dedicated API module:

```text
src/
├── api/
│   └── studentApi.js
├── components/
│   ├── StudentCard.jsx
│   ├── StudentList.jsx
│   └── ...
└── App.jsx
```

Example `studentApi.js` implementation:

```javascript
export async function getStudents() {
  const response = await fetch("/api/students");

  if (!response.ok) {
    throw new Error(`Failed to fetch students: ${response.status}`);
  }

  return response.json();
}
```

This creates a clean boundary:

```text
React component
      |
studentApi.js
      |
     HTTP
      |
   FastAPI
```

This is the frontend equivalent of the Repository boundary built on the backend.

## Exercise 4: Replace Mock Data

The previous data flow was:

```text
App -> mockStudents.js
```

The new data flow is:

```text
App -> getStudents() -> FastAPI
```

Remove the mock array as the source of the rendered student list. The mock file can remain temporarily for comparison, but the UI should now be driven by real API data.

## Exercise 5: Add a Loading State

In `App.jsx`, add state for the students, loading status, and errors:

```javascript
const [students, setStudents] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

Render a loading message while the request is in progress:

```jsx
{
  loading && <p>Loading students...</p>;
}
```

The UI should not show an empty student list while the request is still running. Loading and empty are different states.

## Exercise 6: Add an Error State

Render a user-facing error message:

```jsx
{
  error && <p>Failed to load students.</p>;
}
```

During development, preserve the actual error message:

```javascript
setError(error.message);
```

Then expose it through an accessible alert:

```jsx
{
  error && <p role="alert">{error}</p>;
}
```

This helps debug the browser-to-API boundary.

## Exercise 7: Fetch on Component Mount

Use `useEffect()` to load students when the component mounts:

```jsx
useEffect(() => {
  async function loadStudents() {
    try {
      setLoading(true);
      setError(null);

      const data = await getStudents();
      setStudents(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  loadStudents();
}, []);
```

The lifecycle is:

```text
App renders
    |
useEffect runs
    |
API request
    |
loading = true
    |
Response received
    |
setStudents(data)
    |
loading = false
    |
React re-renders
```

React documentation presents manual data fetching inside Effects as one possible client-side approach. It also discusses its limitations and the need to handle stale or irrelevant responses carefully. For this small learning application, this approach is appropriate.

## Exercise 8: Add an Empty State

An empty state is different from a loading state. Render it only after loading completes, no error exists, and the API returns no students:

```jsx
{
  !loading && !error && students.length === 0 && <p>No students found.</p>;
}
```

The application should explicitly understand these states:

- **Loading:** The request is still running.
- **Error:** The request failed.
- **Empty:** The request succeeded but returned no students.
- **Data:** The request succeeded and returned students.

This is an important enterprise UI pattern.

## Exercise 9: Preserve Existing Student Components

Do not rewrite the presentation layer just because the data source changed. The component structure should remain:

```text
StudentList -> StudentCard
```

Only the source of the students changes.

Previous flow:

```text
mockStudents -> StudentList -> StudentCard
```

Current flow:

```text
FastAPI JSON -> students state -> StudentList -> StudentCard
```

Presentation components should barely care where the data came from. That separation is the payoff from the existing component architecture.

## Exercise 10: Configure CORS Properly

Run the applications on separate local origins:

```text
React:  http://localhost:5173
FastAPI: http://localhost:8000
```

Call the backend directly. If the browser reports a CORS error, inspect the browser console and network request. Then configure FastAPI's `CORSMiddleware` for local development:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Do not blindly use the following configuration for a production authenticated application:

```python
allow_origins=["*"]
```

FastAPI's `CORSMiddleware` configuration controls allowed origins, methods, headers, and credentials.

## Exercise 11: Compare a Direct URL with a Vite Proxy

First test a direct backend request:

```text
React -> http://localhost:8000/students
```

Then configure a Vite development proxy and use:

```text
React -> /api/students -> Vite proxy -> http://localhost:8000/students
```

The Vite proxy runs in the development server and routes matching paths to a configured target.

Document the following:

1. Why did we use the proxy?
2. What local development problem does it solve?
3. Does it replace production CORS configuration?

The answer to the third question is **no**.

## Exercise 12: Network Debugging Drill

Open browser DevTools with `F12`, select the **Network** tab, and reload the React page.

Inspect the following request details:

- Request URL
- Request method
- Status code
- Request headers
- Response headers
- Response body
- Timing

You should be able to trace the complete flow:

```text
Browser
  |
HTTP request
  |
FastAPI
  |
HTTP response
  |
React state
  |
UI
```

This browser-to-API tracing skill is part of the everyday debugging work of a full-stack engineer.
