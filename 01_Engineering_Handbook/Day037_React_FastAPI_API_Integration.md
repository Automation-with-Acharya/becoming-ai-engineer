# Day 037 — React ↔ FastAPI API Integration

**Project:** Project ₹50L — Student Management System  
**Week:** 6 — Modern Backend + Frontend Integration  
**Day:** 037  
**Session date:** 16 September 2026  
**Focus:** React ↔ FastAPI API integration, `fetch()`, asynchronous UI state, loading/error/empty states, CORS, and Vite development proxy  
**Previous foundation:** Day 036 — React + Vite fundamentals, reusable components, props, state, derived values, stable list keys, and basic DSA with `Map` / `Set`

---

# 1. Day 037 Objective

The goal of Day 037 is to move the Student Management frontend from **static mock data** to **real backend data**.

Day 036 established the React component tree:

```text
App
├── Header
├── StudentSummary
├── StudentList
│   └── StudentCard
└── Footer
```

Day 037 adds the network boundary:

```text
React UI
   │
   ▼
API Module
   │
   ▼
HTTP / Fetch
   │
   ▼
FastAPI
   │
   ▼
Service
   │
   ▼
Repository
   │
   ▼
PostgreSQL
```

The important engineering shift is:

> **The UI no longer owns the source of truth. The backend does.**

The frontend becomes a client of the existing REST API.

---

# 2. What Changed From Day 036?

On Day 036, the Student Management UI used mock data and focused on React fundamentals.

The main concepts were:

- component composition,
- props,
- state ownership,
- event → state update → re-render,
- derived values,
- stable list keys.

Day 037 keeps those components but changes **where the student data comes from**.

```text
DAY 036

mockStudents.js
      │
      ▼
    App
      │
      ▼
StudentList
      │
      ▼
StudentCard
```

becomes:

```text
DAY 037

FastAPI /students/
       │
       ▼
studentApi.js
       │
       ▼
     App
       │
       ▼
StudentList
       │
       ▼
StudentCard
```

This is the first real frontend/backend integration point in the roadmap.

---

# 3. Why API Integration Matters

A frontend without an API boundary is only a presentation demo.

A real application normally needs to:

- read server-side state,
- submit changes,
- handle network latency,
- handle server failures,
- handle empty datasets,
- distinguish transport errors from application errors,
- authenticate requests later,
- evolve independently from the backend.

The browser therefore needs a reliable contract with the backend.

For this project, the backend already exposes a `/students/` router and returns JSON student records from the FastAPI service layer.

The backend's current architecture remains layered:

```text
Browser
  │
  │ HTTP
  ▼
FastAPI Router
  │
  │ Depends()
  ▼
StudentService
  │
  ▼
PostgresStudentRepository
  │
  ▼
Connection Pool
  │
  ▼
PostgreSQL
```

The frontend should not know about the Repository or PostgreSQL layers.

---

# 4. The Browser ↔ FastAPI Request Lifecycle

A typical GET request now follows this path:

```text
User opens React app
        │
        ▼
React component renders
        │
        ▼
useEffect starts request
        │
        ▼
studentApi.getStudents()
        │
        ▼
fetch("/api/students")
        │
        ▼
Vite proxy OR direct HTTP request
        │
        ▼
FastAPI /students/
        │
        ▼
StudentService
        │
        ▼
PostgreSQL
        │
        ▼
JSON response
        │
        ▼
setStudents(data)
        │
        ▼
React re-render
        │
        ▼
StudentList / StudentCard
```

This is the key mental model for Day 037.

---

# 5. `fetch()` — The Browser Network Primitive

The browser's Fetch API provides the mechanism for making HTTP requests from JavaScript.

```javascript
const response = await fetch("http://localhost:8000/students/");
const data = await response.json();
```

A critical point:

`fetch()` does **not** automatically reject because the server returned `404`, `400`, or `500`.

The promise is fulfilled with a `Response`, so application code should explicitly inspect `response.ok` or `response.status`. `Response.ok` is `true` for HTTP statuses in the `200–299` range. citeturn247982search2turn247982search3

A safe basic pattern is:

```javascript
export async function getStudents() {
  const response = await fetch("/api/students");

  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }

  return response.json();
}
```

This creates a clean boundary:

```text
HTTP response
     │
     ├── 2xx → return parsed data
     │
     └── non-2xx → throw error
```

---

# 6. Why Create `studentApi.js`?

Do not scatter network calls across components.

Avoid:

```javascript
// StudentList.jsx
fetch("http://localhost:8000/students/");

// StudentSummary.jsx
fetch("http://localhost:8000/students/");

// StudentCard.jsx
fetch("http://localhost:8000/students/");
```

Prefer:

```text
Components
    │
    ▼
studentApi.js
    │
    ▼
HTTP
```

Example:

```javascript
// src/api/studentApi.js

export async function getStudents() {
  const response = await fetch("/api/students");

  if (!response.ok) {
    throw new Error(`Unable to load students (${response.status})`);
  }

  return response.json();
}
```

The API module becomes the frontend's **HTTP boundary**.

Benefits:

- one place for endpoint definitions,
- easier testing,
- easier future authentication headers,
- easier error normalization,
- easier migration to an API client library,
- components remain focused on presentation and state.

This mirrors the backend architecture already used in the project:

```text
Frontend
Component
   ↓
API Module

Backend
Router
   ↓
Service
   ↓
Repository
```

Each boundary hides implementation details from the layer above it.

---

# 7. `useEffect` — Synchronizing React With an External System

React's `useEffect` is designed to synchronize a component with an external system, such as a network connection, browser API, or other system outside React's own rendering model. React's current documentation also shows manual data fetching inside Effects as a valid client-side technique, while warning that larger applications often benefit from framework-level fetching or client-side caching. citeturn247982search1

For the Student Management learning project, the conceptual pattern is:

```javascript
useEffect(() => {
  // start network request
}, []);
```

An empty dependency array means the Effect is tied to the component's mount lifecycle for this simple case.

A practical implementation is:

```javascript
useEffect(() => {
  async function loadStudents() {
    try {
      const data = await getStudents();
      setStudents(data);
    } catch (error) {
      setError(error.message);
    }
  }

  loadStudents();
}, []);
```

The important principle is not memorizing the syntax.

The important principle is understanding the responsibility:

> React renders UI. The Effect coordinates an external side effect such as a network request.

---

# 8. Why `async` Should Not Be Put Directly on the Effect Callback

Avoid:

```javascript
useEffect(async () => {
  // ...
}, []);
```

The Effect callback itself is expected to return either nothing or a cleanup function. An `async` function returns a Promise instead.

Prefer:

```javascript
useEffect(() => {
  async function loadStudents() {
    // async work
  }

  loadStudents();
}, []);
```

This preserves the Effect contract while still allowing `await` inside the nested function.

---

# 9. The Four UI States

A network-backed UI should not assume that data is instantly available.

The core state model is:

```text
                DATA REQUEST
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
       Loading      Error      Success
                                  │
                        ┌─────────┴─────────┐
                        ▼                   ▼
                      Empty               Data
```

The four user-visible states are:

| State   | Meaning                                   | Example UI                |
| ------- | ----------------------------------------- | ------------------------- |
| Loading | Request is in progress                    | `Loading students...`     |
| Error   | Request failed                            | `Unable to load students` |
| Empty   | Request worked, but result has no records | `No students found`       |
| Data    | Request worked and records exist          | Student cards             |

This distinction is important.

**Empty is not an error.**

A successful response with `[]` means the backend worked and there are simply no records.

---

# 10. Recommended React State Model

For this learning project:

```javascript
const [students, setStudents] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError] = useState(null);
```

The flow becomes:

```text
Initial render
    │
    ▼
loading = true
    │
    ▼
fetch()
    │
    ├── success + data → students = data
    │
    ├── success + []   → students = []
    │
    └── failure        → error = message
    │
    ▼
loading = false
```

A clean implementation pattern is:

```javascript
useEffect(() => {
  async function loadStudents() {
    setLoading(true);
    setError(null);

    try {
      const data = await getStudents();
      setStudents(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  loadStudents();
}, []);
```

The `finally` block is particularly important because both success and failure must leave the UI out of the loading state.

---

# 11. UI Rendering Order

A practical rendering order is:

```javascript
if (loading) {
  return <p>Loading students...</p>;
}

if (error) {
  return <p role="alert">{error}</p>;
}

if (students.length === 0) {
  return <p>No students found.</p>;
}

return <StudentList students={students} />;
```

This creates explicit behavior instead of leaving the UI ambiguous.

Accessibility also improves when error feedback uses an appropriate semantic element such as:

```jsx
<p role="alert">Unable to load students.</p>
```

---

# 12. The `StudentSummary` Component Still Uses Derived Data

The Day 036 lesson about derived state remains valid after API integration.

Do **not** create separate state for:

```javascript
const [total, setTotal] = useState(0);
const [active, setActive] = useState(0);
const [inactive, setInactive] = useState(0);
```

Instead derive the values from the current student collection:

```javascript
const total = students.length;
const active = students.filter((student) => student.active).length;
const inactive = total - active;
```

The backend owns the records.

React stores the collection it has received.

The summary is a projection of that collection.

```text
Backend data
     │
     ▼
students[]
     │
     ├── StudentList
     └── StudentSummary
```

One source of truth is easier to reason about than duplicated state.

---

# 13. Actual FastAPI CORS Configuration in the Project

The Student Management backend already includes `CORSMiddleware` and explicitly allows the Vite development origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This is significant because the frontend and backend are separate origins during local development.

FastAPI's documentation defines an origin using the combination of protocol, host, and port. Therefore `http://localhost:5173` and `http://localhost:8000` are different origins even though both use `localhost`. citeturn219069search0

The backend must therefore explicitly permit the frontend origin.

---

# 14. What CORS Actually Solves

CORS is a **browser security mechanism** that controls whether browser JavaScript is allowed to access resources across origins. The server communicates the allowed policy through HTTP response headers. citeturn247982search4

Conceptually:

```text
React App
http://localhost:5173
        │
        │ cross-origin request
        ▼
FastAPI
http://localhost:8000
        │
        │ CORS policy
        ▼
Browser decides whether JS
may access the response
```

CORS is not:

- an authentication mechanism,
- a database security feature,
- an API permission system,
- a replacement for JWT/session authorization.

It answers a different question:

> **Which browser origins are allowed to make and read cross-origin requests?**

---

# 15. CORS Preflight

Some cross-origin requests trigger an `OPTIONS` preflight request before the actual request.

The browser effectively asks:

```text
OPTIONS /students/

Origin: http://localhost:5173
Access-Control-Request-Method: GET
```

The server must respond with compatible CORS headers.

FastAPI's `CORSMiddleware` handles these preflight requests when configured correctly. Its documentation identifies preflights as `OPTIONS` requests containing `Origin` and `Access-Control-Request-Method`. citeturn219069search0

MDN also documents preflight as an `OPTIONS` request used to determine whether the actual cross-origin request is allowed. citeturn247982search4

---

# 16. Why Explicit Origins Are Better Than Blind Wildcards

A common development shortcut is:

```python
allow_origins=["*"]
```

That may be acceptable for controlled experiments, but production systems should normally specify the real allowed origins.

FastAPI's current documentation specifically notes that wildcard handling has restrictions when credentials are involved. In particular, when `allow_credentials=True`, the origins/methods/headers cannot all be represented by `*`; explicit configuration is required. citeturn219069search0

The current project already uses an explicit local Vite origin:

```text
http://localhost:5173
```

That is a good development pattern because the policy expresses exactly which local frontend is expected to communicate with the API.

---

# 17. Vite Development Proxy

Vite supports development-time proxy rules through `server.proxy`. Requests whose path matches the configured key can be forwarded to another server. citeturn247982search0

Example:

```javascript
// vite.config.js

export default defineConfig({
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

Then frontend code can use:

```javascript
fetch("/api/students/");
```

instead of embedding the backend host in every component.

The development flow becomes:

```text
Browser
  │
  │ /api/students/
  ▼
Vite Dev Server
  │
  │ proxy
  ▼
FastAPI
http://localhost:8000/students/
```

---

# 18. CORS vs Vite Proxy — Do Not Confuse Them

These solve different problems.

| Topic                                | CORS                            | Vite Proxy                                   |
| ------------------------------------ | ------------------------------- | -------------------------------------------- |
| Purpose                              | Browser cross-origin permission | Development request forwarding               |
| Controlled by                        | Backend/server policy           | Vite dev server                              |
| Typical production relevance         | High                            | Dev-only by default                          |
| Changes browser origin relationship? | No                              | Can make browser request same-origin to Vite |
| Solves authentication?               | No                              | No                                           |
| Main benefit                         | Secure browser access policy    | Cleaner local development                    |

A useful mental model:

```text
CORS
Server says:
"This browser origin is allowed."

Vite Proxy
Dev server says:
"I'll forward this local path to your backend."
```

A Vite proxy should not be treated as the production security boundary.

---

# 19. The Most Important Debugging Tool: Browser DevTools

Day 037 introduces the Network tab as an engineering tool.

When the UI is not loading data, inspect:

```text
Browser DevTools
      │
      ▼
Network
      │
      ├── Request URL
      ├── Request Method
      ├── Status Code
      ├── Request Headers
      ├── Response Headers
      ├── Response Body
      └── Timing
```

A disciplined debugging sequence is:

```text
1. Was the request sent?
        │
        ├── No → React / Effect / API module issue
        │
        └── Yes
             │
             ▼
2. What status code?
             │
             ├── 2xx → inspect JSON / state update
             ├── 4xx → client/request problem
             ├── 5xx → backend problem
             └── blocked/CORS → browser policy problem
```

Then inspect the FastAPI logs and Swagger UI independently.

---

# 20. Troubleshooting Matrix

| Symptom                              | Likely area                 | First check                                   |
| ------------------------------------ | --------------------------- | --------------------------------------------- |
| No request appears in Network        | React lifecycle / code path | `useEffect`, component mount                  |
| `404`                                | URL/path mismatch           | FastAPI `/docs` and Request URL               |
| `500`                                | Backend                     | FastAPI logs / traceback                      |
| CORS error                           | Browser policy              | Response CORS headers + allowed origin        |
| Request succeeds but cards are empty | State/data shape            | `response.json()` and console/network payload |
| Spinner never stops                  | State lifecycle             | `finally { setLoading(false) }`               |
| Error UI never appears               | Error handling              | `response.ok` check + `catch`                 |
| Proxy request fails                  | Vite config                 | `server.proxy`, target, rewrite               |
| UI shows old mock students           | Data source not replaced    | Search for remaining `mockStudents` imports   |

---

# 21. API Contract Thinking

Frontend/backend integration becomes much easier when the API response contract is explicit.

The existing FastAPI `/students/` endpoint returns a list of student response models.

Conceptually:

```json
[
  {
    "id": 1,
    "name": "Alice",
    "age": 21,
    "city": "Ahmedabad",
    "email": "alice@example.com"
  }
]
```

The frontend should map against the actual backend contract rather than inventing a new shape.

This matters because the frontend's expectations become part of the integration contract.

```text
Backend response schema
          │
          ▼
Frontend API module
          │
          ▼
React state
          │
          ▼
Components
```

When the contract changes, this chain is where breakage should become visible quickly.

---

# 22. Data Fetching Architecture for This Project

The intended Day 037 structure is:

```text
student-management-ui/
│
├── src/
│   ├── api/
│   │   └── studentApi.js
│   │
│   ├── components/
│   │   ├── Header.jsx
│   │   ├── StudentSummary.jsx
│   │   ├── StudentList.jsx
│   │   ├── StudentCard.jsx
│   │   └── Footer.jsx
│   │
│   ├── data/
│   │   └── mockStudents.js      ← legacy learning artifact
│   │
│   ├── App.jsx
│   └── main.jsx
│
└── vite.config.js
```

The production flow should no longer make `mockStudents.js` the primary source.

The preferred dependency direction is:

```text
App
 │
 └── studentApi
       │
       └── HTTP
```

Components receive data through props rather than knowing how the network works.

---

# 23. Complete Reference Implementation Pattern

A compact example combining the day's concepts:

```jsx
import { useEffect, useState } from "react";
import { getStudents } from "./api/studentApi";

function App() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadStudents() {
      setLoading(true);
      setError(null);

      try {
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

  if (loading) {
    return <p>Loading students...</p>;
  }

  if (error) {
    return <p role="alert">{error}</p>;
  }

  if (students.length === 0) {
    return <p>No students found.</p>;
  }

  return <StudentList students={students} />;
}
```

API module:

```javascript
export async function getStudents() {
  const response = await fetch("/api/students/");

  if (!response.ok) {
    throw new Error(`Unable to load students (${response.status})`);
  }

  return response.json();
}
```

The exact endpoint path should always match the backend route actually deployed.

---

# 24. Why Not Fetch Inside `StudentCard`?

`StudentCard` is a presentation component.

Its job is to answer:

> "How do I display one student?"

It should not answer:

> "Where does the student data come from?"

That distinction preserves separation of concerns.

```text
App / container-level responsibility
        │
        ├── data fetching
        ├── loading state
        └── error state

Presentation responsibility
        │
        ├── StudentList
        └── StudentCard
```

This architecture also makes later testing easier because presentation components can receive test data directly through props.

---

# 25. Race Conditions and Cleanup — The Next Level

For the Day 037 learning objective, a simple mount-time GET is enough.

However, React's current documentation highlights an important limitation of manual Effect-based fetching: more complicated data flows can introduce race conditions, repeated requests, network waterfalls, and cache/preload problems. citeturn247982search1

One defensive approach is to cancel or ignore obsolete requests when dependencies change.

Conceptually:

```text
Request A starts
     │
     ▼
User changes selection
     │
     ▼
Request B starts
     │
     ├── B returns first
     └── A returns later
```

Without protection, stale Request A could overwrite newer state.

This is not the primary Day 037 implementation target, but it is an important production engineering concept to carry forward.

---

# 26. Production Perspective: Manual `useEffect` Fetching Has Limits

React's current documentation explicitly says that fetching data directly inside Effects is common in client-side applications but can become repetitive and makes concerns such as caching, preloading, and deduplication harder. It points toward framework data-loading mechanisms or client-side caching approaches for larger applications. citeturn247982search1

For this project, manual `fetch()` is appropriate because the objective is to understand the underlying mechanics.

Later, once the fundamentals are solid, an enterprise frontend may introduce a data-fetching/cache abstraction.

The engineering sequence is therefore:

```text
Learn the primitive
      ↓
Understand the lifecycle
      ↓
Recognize the limitations
      ↓
Adopt higher-level abstraction when complexity justifies it
```

Do not jump to a library before understanding the problem it is solving.

---

# 27. Enterprise Comparison

## React + FastAPI

```text
React
  ↓
API Client / Hook
  ↓
HTTP
  ↓
FastAPI
  ↓
Service
  ↓
Repository
  ↓
PostgreSQL
```

## React + ASP.NET Core

```text
React
  ↓
API Client / Hook
  ↓
HTTP
  ↓
ASP.NET Core Controller / Minimal API
  ↓
Service
  ↓
Repository / EF Core
  ↓
SQL Server / PostgreSQL
```

## Angular + ASP.NET Core

```text
Angular Component
  ↓
Service / HttpClient
  ↓
HTTP
  ↓
ASP.NET Core
  ↓
Application Layer
  ↓
Repository
  ↓
Database
```

The technologies differ, but the engineering ideas remain similar:

| Concern             | React                            | Angular                                      | FastAPI / ASP.NET Core backend     |
| ------------------- | -------------------------------- | -------------------------------------------- | ---------------------------------- |
| UI composition      | Components                       | Components                                   | Not applicable                     |
| Client HTTP         | `fetch`, libraries, hooks        | `HttpClient`                                 | Server receives HTTP               |
| State               | Local state + other abstractions | Component/service state + other abstractions | Server-side application state      |
| Validation          | Client UX validation             | Client UX validation                         | Authoritative server validation    |
| CORS                | Browser constraint               | Browser constraint                           | Server policy                      |
| Dependency boundary | API module / hook                | Service                                      | DI container / dependency provider |
| Testing seam        | Props/API abstraction            | Services/DI                                  | DI, mocks, integration tests       |

The key transferable skill is not memorizing framework syntax.

It is recognizing the same architecture across different stacks.

---

# 28. CORS and Security — Enterprise View

A production API should treat CORS as one part of a broader security model.

```text
Browser Origin Policy
        │
        ▼
CORS
        │
        ▼
Authentication
        │
        ▼
Authorization
        │
        ▼
Input Validation
        │
        ▼
Business Rules
        │
        ▼
Database Constraints
```

CORS does not replace authentication or authorization.

For the future Student Management application, JWT authentication learned in earlier weeks will eventually sit alongside the CORS policy.

---

# 29. Common Mistakes

## Mistake 1 — Treating `fetch()` 404/500 as a rejected Promise

Incorrect assumption:

```text
404 → catch()
```

Actual behavior:

```text
404 → fulfilled Response
     → response.ok === false
```

Check `response.ok` / `response.status`. citeturn247982search2turn247982search3

---

## Mistake 2 — Putting API calls in every component

This duplicates endpoint knowledge and spreads networking concerns throughout the UI.

Keep an API boundary.

---

## Mistake 3 — Mixing loading, error, and empty states

These are separate conditions.

```text
Loading ≠ Error ≠ Empty ≠ Data
```

---

## Mistake 4 — Fixing CORS with `no-cors`

`no-cors` is not a general browser-side solution for normal application APIs. The result becomes opaque and JavaScript cannot inspect the response body or normal response metadata. MDN explicitly warns against using it as a normal application strategy. citeturn247982search5

Fix the server-side CORS policy instead.

---

## Mistake 5 — Allowing every origin in production without a reason

Use explicit origins when the environment is known.

---

## Mistake 6 — Hardcoding backend URLs everywhere

Bad:

```javascript
fetch("http://localhost:8000/students/");
```

spread across multiple components.

Prefer an API module and environment-aware configuration/proxy strategy.

---

## Mistake 7 — Keeping mock data active after real API integration

Once the backend is the source of truth, the development flow should make it obvious whether the UI is reading the real service or stale mock data.

---

# 30. Engineering Sprinkle

## Debugging Tip

When data does not appear, do not start by rewriting React components.

Trace the request from the outside in:

```text
Browser Network tab
       ↓
Request URL
       ↓
HTTP status
       ↓
Response body
       ↓
FastAPI logs
       ↓
Swagger endpoint
       ↓
Database/query
```

This is faster than debugging by guesswork.

## Production Practice

Keep these concerns separate:

```text
UI rendering
     │
     ▼
Client state
     │
     ▼
API abstraction
     │
     ▼
Transport concerns
```

Separation makes later introduction of authentication, retries, caching, telemetry, and automated tests much easier.

## Interview Insight

A strong interview answer should not stop at:

> "I used `useEffect` to call the API."

A better engineering explanation includes:

```text
API boundary
→ lifecycle trigger
→ loading state
→ error handling
→ response validation
→ state update
→ re-render
→ empty-state handling
→ CORS policy
```

That demonstrates understanding instead of syntax recall.

---

# 31. DSA Sprinkle — Day 037

The daily DSA habit remains intentionally small and practical.

## Problem A — Frequency Counter

Input:

```text
["python", "react", "python", "sql", "react", "python"]
```

Goal:

```text
{
  python: 3,
  react: 2,
  sql: 1
}
```

### JavaScript

```javascript
const counts = new Map();

for (const item of items) {
  counts.set(item, (counts.get(item) ?? 0) + 1);
}
```

### Python

```python
counts = {}

for item in items:
    counts[item] = counts.get(item, 0) + 1
```

**Complexity:** `O(n)` time and `O(k)` space, where `k` is the number of distinct values.

## Problem B — Group Students by City

Given:

```javascript
[
  { name: "A", city: "Ahmedabad" },
  { name: "B", city: "Mumbai" },
  { name: "C", city: "Ahmedabad" },
];
```

Target structure:

```text
Ahmedabad → [A, C]
Mumbai    → [B]
```

The key interview pattern is:

```text
lookup key
    ↓
create bucket if absent
    ↓
append item
```

This reinforces practical `Map` / dictionary usage that frequently appears in backend and full-stack interview problems.

---

# 32. Interview Questions

### Q1. Why do we use `useEffect` for API calls?

Because the network request is an external side effect relative to React's rendering process. `useEffect` provides a lifecycle mechanism for synchronizing the component with that external system. citeturn247982search1

### Q2. Why should the Effect callback not be declared `async` directly?

Because an async function returns a Promise, while an Effect callback is expected to return either nothing or a cleanup function.

### Q3. Does `fetch()` throw automatically for HTTP 404 or 500?

No. The Promise generally resolves to a `Response`; application code should inspect `response.ok` or `response.status`. citeturn247982search2turn247982search3

### Q4. What is CORS?

CORS is a browser-enforced mechanism using HTTP headers that controls whether a web application from one origin may access resources from another origin. citeturn247982search4

### Q5. What is an origin?

An origin is determined by protocol, host, and port. Therefore `localhost:5173` and `localhost:8000` are different origins. citeturn219069search0

### Q6. What is a CORS preflight?

It is an `OPTIONS` request used by the browser to ask whether a cross-origin request is permitted before sending the actual request in cases where preflight is required. citeturn247982search4turn219069search0

### Q7. Why use an API module instead of `fetch()` directly in components?

To centralize endpoint and transport concerns, reduce duplication, improve testability, and keep UI components focused on presentation/state.

### Q8. What is the difference between loading and empty?

Loading means the request has not finished. Empty means the request finished successfully but returned no records.

### Q9. What is the difference between CORS and authentication?

CORS controls browser cross-origin access. Authentication establishes identity. They solve different problems.

### Q10. What does Vite `server.proxy` do?

It forwards matching development requests from the Vite dev server to another server, making local development easier and often avoiding browser-visible cross-origin calls during development. citeturn247982search0

### Q11. Does a Vite proxy replace production CORS configuration?

Not in general. Vite's `server.proxy` is a development-server feature; production architecture needs its own frontend/backend routing and browser security policy. citeturn247982search0

### Q12. Why should `StudentCard` not fetch its own student data?

Because it is a presentation component. The container/application layer should own data fetching and pass the resulting data through props.

### Q13. Why is `finally()` useful in a fetch flow?

It provides one place to end the loading state regardless of success or failure.

### Q14. Why can manual data fetching in Effects become problematic at scale?

React's current documentation highlights repeated boilerplate, lack of caching/preloading, potential network waterfalls, and race-condition concerns. Larger applications often move data loading into framework or client-cache abstractions. citeturn247982search1

---

# 33. Cheat Sheet

```text
React component
      │
      ▼
useEffect()
      │
      ▼
API module
      │
      ▼
fetch()
      │
      ▼
Response
      │
      ├── !ok → throw
      │
      └── ok  → response.json()
                     │
                     ▼
                 setState()
                     │
                     ▼
                 re-render
```

## UI state

```text
loading
  │
  ├── error
  │
  └── success
       ├── empty
       └── data
```

## CORS

```text
Frontend Origin
     │
     ▼
FastAPI CORSMiddleware
     │
     ├── allowed → browser may expose response
     └── denied  → browser blocks JS access
```

## Vite Proxy

```text
Browser
  │
  └── /api/*
        ↓
     Vite dev server
        ↓
     FastAPI target
```

---

# 34. Why Does This Exist?

## What problem does it solve?

Before Day 037, the frontend could display student data but did not rely on the real backend.

That means the UI was disconnected from the application's source of truth.

API integration solves that by connecting the frontend to the production-style backend already built in previous weeks.

```text
Before

Mock Data → React

After

React → HTTP → FastAPI → Service → Repository → PostgreSQL
```

The result is a real client/server application rather than an isolated frontend demo.

---

## Who depends on it?

```text
User
  │
  ▼
React UI
  │
  ▼
API Module
  │
  ▼
HTTP
  │
  ▼
FastAPI
  │
  ▼
Business Logic
  │
  ▼
Repository
  │
  ▼
PostgreSQL
```

Every interactive full-stack feature ultimately depends on a reliable client/server contract.

---

## Who should NOT depend on it?

Presentation components should not depend directly on:

- database details,
- PostgreSQL queries,
- FastAPI repository internals,
- connection pool implementation.

`StudentCard` should know about a student object, not how that object was retrieved.

---

## Backend architectural equivalent

The backend already follows the same abstraction idea:

```text
Router
  ↓
Service
  ↓
Repository
  ↓
Database
```

The frontend should adopt the corresponding boundary:

```text
Component
  ↓
API Module
  ↓
HTTP
```

This is the same software engineering idea expressed at another layer:

> **Hide implementation details behind stable interfaces.**

---

# 35. Engineering Evolution

The Student Management project has evolved from a simple CLI into a layered full-stack system.

```text
Days 1–7
Python + CLI + PostgreSQL
        │
        ▼
Days 8–14
Repository + Service + FastAPI
        │
        ▼
Days 15–21
JWT + Middleware + Logging + Exceptions + Config + Transactions + Pool
        │
        ▼
Days 22–29
Indexing + Docker + Compose + Health Checks + Deployment Practices
        │
        ▼
Days 30–35
Advanced SQL + Query Optimization + Automated Testing
        │
        ▼
Day 036
React + Vite + Component Architecture + State
        │
        ▼
Day 037
React ↔ FastAPI Integration
        │
        ▼
Next
React Forms + CRUD + Authentication + Dashboard
```

The important architectural pattern is that every new layer builds on the previous one.

We are not restarting the project.

We are extending the same system.

---

# 36. Revision Checklist

- [ ] Explain the browser → API → database request lifecycle.
- [ ] Explain why `fetch()` belongs behind an API abstraction.
- [ ] Know why `response.ok` must be checked explicitly.
- [ ] Explain why `useEffect` is suitable for a simple client-side fetch.
- [ ] Explain why an Effect callback should not itself be `async`.
- [ ] Implement `loading`, `error`, `empty`, and `data` UI states.
- [ ] Explain why `finally()` is useful for loading state cleanup.
- [ ] Explain why empty results are not errors.
- [ ] Define CORS in terms of browser origins and response headers.
- [ ] Define an origin using protocol + host + port.
- [ ] Explain CORS preflight and the role of `OPTIONS`.
- [ ] Explain the current FastAPI `CORSMiddleware` configuration used by the project.
- [ ] Explain the difference between CORS and authentication.
- [ ] Explain the role of Vite `server.proxy`.
- [ ] Explain why a Vite proxy is not a production security model.
- [ ] Use browser DevTools Network to debug an API request.
- [ ] Explain why `StudentCard` should remain a presentation component.
- [ ] Explain the difference between mock data and backend source-of-truth data.
- [ ] Solve a frequency-counter problem with a hash map / dictionary.
- [ ] Group records by a key using `Map` / dictionary buckets.

---

# 37. Final Key Takeaways

- React now consumes real backend data instead of relying on mock data as the primary source.
- `fetch()` provides the network request primitive, but non-2xx responses must be checked explicitly. citeturn247982search2turn247982search3
- `useEffect` provides a simple way to coordinate a client-side fetch with the component lifecycle. citeturn247982search1
- A dedicated API module keeps network concerns out of presentation components.
- A robust UI distinguishes loading, error, empty, and data states.
- CORS is a browser access-control mechanism, not an authentication system. citeturn247982search4
- `http://localhost:5173` and `http://localhost:8000` are different origins because their ports differ. citeturn219069search0
- FastAPI's `CORSMiddleware` handles the server-side CORS policy and preflight behavior. citeturn219069search0
- Vite's `server.proxy` is a development-time request-forwarding tool. citeturn247982search0
- Browser DevTools Network is a first-class debugging tool for full-stack applications.
- The Day 036 architecture is preserved; Day 037 simply connects it to the real backend.
- Manual Effect-based fetching is the correct learning primitive here, but larger applications may eventually need a stronger data-loading/cache abstraction. citeturn247982search1

---

# 38. Official References

1. **React — `useEffect`**  
   https://react.dev/reference/react/useEffect

2. **Vite — Server Options / `server.proxy`**  
   https://vite.dev/config/server-options

3. **FastAPI — CORS**  
   https://fastapi.tiangolo.com/tutorial/cors/

4. **MDN — Cross-Origin Resource Sharing (CORS)**  
   https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS

5. **MDN — Using Fetch**  
   https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

6. **MDN — `Response.ok`**  
   https://developer.mozilla.org/en-US/docs/Web/API/Response/ok

**Reference status:** Official documentation checked during handbook preparation on 23 September 2026.

---

# 39. Day 037 Completion Standard

Day 037 is conceptually complete when you can explain, without referring to notes:

```text
React component
   ↓
useEffect
   ↓
API module
   ↓
fetch
   ↓
response.ok
   ↓
JSON
   ↓
state update
   ↓
loading/error/empty/data UI
   ↓
Vite proxy / CORS
   ↓
FastAPI
   ↓
Service
   ↓
Repository
   ↓
PostgreSQL
```

The objective is not merely to make one request work.

The objective is to understand the entire request lifecycle and the responsibility of every layer.

---

**Status:** ✅ Day 037 Engineering Handbook Complete
