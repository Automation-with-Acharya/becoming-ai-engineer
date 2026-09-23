# React & FastAPI — Exercises Answer Sheet

**Day:** 037  
**Date:** 2026-09-23  
**Project:** `MiniProject_Student_Management / frontend / student-management-ui`  
**Stack:** React 19 + Vite 8 + FastAPI backend

---

## Exercise 1: Verify the FastAPI Backend

**Steps taken:**

1. Started the backend: `python app.py` → Uvicorn on `http://localhost:8000`
2. Opened Swagger UI at `http://localhost:8000/docs`
3. Confirmed `GET /students/` returns HTTP `200 OK` with a student array

**Endpoint confirmed:**

```http
GET /students/
```

Router prefix is `/students` (defined in `routers/students.py` with `prefix="/students"`).

**Baseline established:**
- ✅ Backend works independently before touching React

---

## Exercise 2: Identify the API Contract

**Real response from `GET /students/`:**

```json
[
  {
    "id": 1,
    "name": "Mayank Acharya",
    "age": 28,
    "city": "Gandhinagar",
    "email": "mayank@example.com"
  }
]
```

**Observations:**
- The backend `Student_response_model` has fields: `id`, `name`, `age`, `city`, `email`
- There is **no `active` field** — the database schema does not track active status
- The mock data from Day 036 added `active` as a frontend-only field
- The `StudentCard` component was updated to handle `active` being `undefined` gracefully

**Rule applied:** React consumes the actual API contract — no invented second format.

---

## Exercise 3: Create an API Module

**File created:** `src/api/studentApi.js`

```javascript
export async function getStudents() {
  const response = await fetch("/api/students");  // Vite proxy rewrites to localhost:8000

  if (!response.ok) {
    throw new Error(`Failed to fetch students: HTTP ${response.status}`);
  }

  return response.json();
}
```

**Boundary created:**

```
React component (App.jsx)
        |
  studentApi.js         ← this file owns all fetch() calls
        |
       HTTP (via Vite proxy)
        |
     FastAPI
```

**Why a dedicated module (mirrors the backend Repository Pattern):**
1. Single place to change base URL, auth headers, or error handling
2. Components stay focused on rendering — they don't know about HTTP
3. The API module is independently testable (mock fetch in unit tests)
4. Same clean-architecture principle as `StudentRepository` on the backend

---

## Exercise 4: Replace Mock Data

**Before (Day 036):**

```
App → mockStudents.js (local array)
```

**After (Day 037):**

```
App → getStudents() → FastAPI /students
```

**Changes:**
- Removed `import students from "./data/mockStudents"` from `App.jsx`
- `students` is now `useState([])` — starts empty, populated by the API
- `mockStudents.js` file kept for reference but no longer imported

**Key insight:** The `StudentList` and `StudentCard` components were **not changed** — they still receive the same `students` prop. The only change is _where that data comes from_.

---

## Exercise 5: Add a Loading State

**State added in `App.jsx`:**

```javascript
const [students, setStudents] = useState([]);
const [loading, setLoading] = useState(true);
const [error, setError]  = useState(null);
```

**JSX rendered while loading:**

```jsx
{loading && (
  <p className="status-message status-message--loading" aria-live="polite">
    ⏳ Loading students…
  </p>
)}
```

**Why loading and empty are different states:**
- **Loading:** The request is still running — the UI doesn't yet know if data exists
- **Empty:** The request finished — the server confirmed there are 0 students

Conflating the two would flash an empty state before data arrives, confusing users.

---

## Exercise 6: Add an Error State

**Error state rendered:**

```jsx
{error && (
  <p className="status-message status-message--error" role="alert">
    ❌ {error}
  </p>
)}
```

**Error captured in the catch block:**

```javascript
} catch (err) {
  setError(err.message);  // Preserves the actual error string for debugging
}
```

**Design decisions:**
- `role="alert"` announces the error to screen readers immediately
- `err.message` is shown directly — useful during development at the browser-to-API boundary
- In production this would be replaced with a generic "Something went wrong" message to avoid leaking internals

---

## Exercise 7: Fetch on Component Mount

**`useEffect` pattern in `App.jsx`:**

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
}, []);  // [] = run once on mount
```

**Why the inner async function?**
`useEffect`'s callback must return `undefined` or a cleanup function. An `async` function returns a Promise, which React cannot use as a cleanup. The solution: define an inner async function and call it immediately.

**The lifecycle:**

```
App renders (loading=true, students=[])
    ↓
useEffect fires (after paint)
    ↓
fetch /api/students
    ↓
setStudents(data) OR setError(err.message)
    ↓
setLoading(false)   ← always (finally)
    ↓
React re-renders with real data / error / empty state
```

---

## Exercise 8: Add an Empty State

**JSX for empty state:**

```jsx
{!loading && !error && students.length === 0 && (
  <p className="status-message status-message--empty">
    📭 No students found.
  </p>
)}
```

**The four UI states the application explicitly handles:**

| State | Condition | UI shown |
|-------|-----------|----------|
| **Loading** | `loading === true` | ⏳ Loading students… |
| **Error** | `error !== null` | ❌ {error message} |
| **Empty** | `!loading && !error && students.length === 0` | 📭 No students found. |
| **Data** | `!loading && !error && students.length > 0` | Summary + Card grid |

This is a standard enterprise UI pattern — never skip any of these four states.

---

## Exercise 9: Preserve Existing Student Components

**Result:** `StudentList` and `StudentCard` were **not rewritten**.

**Previous flow:**

```
mockStudents → StudentList → StudentCard
```

**Current flow:**

```
FastAPI JSON → students state → StudentList → StudentCard
```

The presentation components don't know or care where the data came from.  
This is the payoff from building a clean component boundary in Day 036.

**Only change to `StudentCard`:** The `active` field handling was made resilient — it now shows a "Status N/A" badge when `active` is `undefined` (since the real API doesn't include that field). This is a minor defensive improvement, not a rewrite.

---

## Exercise 10: Configure CORS Properly

**CORS was already correctly configured** in `main.py` (Day 016):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Origins:**
- React dev server: `http://localhost:5173`
- FastAPI backend: `http://localhost:8000`

**Why not `allow_origins=["*"]`?**
- `["*"]` with `allow_credentials=True` is rejected by the browser (CORS spec)
- In a production authenticated app, wildcard origins allow any domain to make credentialed requests — a security risk
- Always specify the exact origin(s) for authenticated APIs

---

## Exercise 11: Compare Direct URL vs Vite Proxy

### Test 1 — Direct URL (no proxy)

**In `studentApi.js`:**
```javascript
const response = await fetch("http://localhost:8000/students");
```

**Result:** Works, but the browser sends a CORS preflight (`OPTIONS`) request before the actual `GET`. The FastAPI CORS middleware must be correctly configured for this to succeed.

---

### Test 2 — Vite Proxy (configured approach)

**In `studentApi.js`:**
```javascript
const response = await fetch("/api/students");  // Vite proxy rewrites to localhost:8000
```

**Vite proxy configuration added to `vite.config.js`:**

```javascript
server: {
  proxy: {
    "/api": {
      target: "http://localhost:8000",
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\/api/, ""),
    },
  },
},
```

**How it works:**

```
Browser (React at :5173)
    GET /api/students
         ↓
Vite Dev Server (proxy layer)
    rewrites: /api/students → /students
    forwards to: http://localhost:8000/students
         ↓
FastAPI backend (:8000)
    responds with JSON
         ↓
Vite proxy returns the response to the browser
```

---

### Q1. Why did we use the proxy?

The proxy keeps the browser happy about same-origin policy during development. The browser sees all requests going to the same origin (`:5173`), so no CORS preflight is triggered by the browser itself.

### Q2. What local development problem does it solve?

It eliminates the need to deal with CORS in the browser for every API request during development. It also allows the `fetch()` URL to be written as a relative path (`/api/students`) — portable across environments.

### Q3. Does it replace production CORS configuration?

**No.** The Vite proxy **only exists in the dev server**. When the React app is built (`npm run build`) and deployed, there is no proxy. In production:
- If the frontend and backend share the same origin (served by the same reverse proxy) — no CORS needed
- If they are on different origins — the FastAPI `CORSMiddleware` is required and must specify the correct production frontend origin

The CORS configuration on the FastAPI backend is not optional for production deployments with separate origins.

---

## Exercise 12: Network Debugging Drill

**Steps in DevTools (F12 → Network tab):**

1. Open `http://localhost:5173` in browser
2. Open DevTools → Network tab → clear existing requests
3. Reload the page

**Request inspected:**

| Field | Value |
|-------|-------|
| **Request URL** | `http://localhost:5173/api/students` (intercepted by proxy) |
| **Forwarded to** | `http://localhost:8000/students` |
| **Request method** | `GET` |
| **Status code** | `200 OK` |
| **Request headers** | `Accept: */*`, `Referer: http://localhost:5173/` |
| **Response headers** | `content-type: application/json`, `x-process-time-ms: ...` |
| **Response body** | `[{"id": 1, "name": "Mayank Acharya", ...}]` |
| **Timing** | Initial: ~2ms (proxy overhead + FastAPI handler) |

**Complete traced flow:**

```
Browser
    |   HTTP GET /api/students
    ↓
Vite Dev Server (proxy strips /api → /students, forwards to :8000)
    |
    ↓   HTTP GET http://localhost:8000/students
FastAPI
    |   Router → Service → Repository → DB → Student_response_model
    ↓
HTTP 200 JSON response
    |
    ↓
React state: setStudents(data)
    |
    ↓
UI re-renders: StudentSummary + StudentCard grid displayed
```

This browser-to-API tracing skill is the core debugging workflow of full-stack engineering.

---

## Files Summary

| File | Status | Exercise(s) |
|------|--------|-------------|
| `src/api/studentApi.js` | **New** | 3, 11 |
| `src/App.jsx` | **Replaced** | 3, 4, 5, 6, 7, 8, 9 |
| `src/App.css` | Modified (+ state styles) | 5, 6, 8 |
| `vite.config.js` | Modified (+ proxy) | 11 |
| `src/components/StudentCard.jsx` | Modified (active field) | 2, 9 |
| `src/components/Header.jsx` | Minor (subtitle updated) | — |
| `src/components/Footer.jsx` | Minor (subtitle updated) | — |
| `main.py` | No change needed | 10 |
| `src/data/mockStudents.js` | Kept, no longer imported | 4 |
