/**
 * studentApi.js
 *
 * Exercise 3: Create an API Module
 *
 * Centralises all HTTP communication with the FastAPI backend.
 * React components NEVER call `fetch()` directly — they import from here.
 *
 * This mirrors the Repository Pattern used on the backend:
 *   - Backend:   StudentRepository abstracts the database layer
 *   - Frontend:  studentApi.js abstracts the HTTP layer
 *
 * The boundary created is:
 *
 *   React component
 *         |
 *   studentApi.js   ← this file
 *         |
 *        HTTP
 *         |
 *      FastAPI
 *
 * Why a dedicated API module?
 * ----------------------------
 * 1. Single place to change the base URL, auth headers, or error handling.
 * 2. Components stay focused on rendering — they don't know about fetch/HTTP.
 * 3. The API module is independently testable (mock fetch in unit tests).
 * 4. Matches the clean-architecture principle already practiced on the backend.
 *
 * URL strategy — Vite proxy (Exercise 11):
 * -----------------------------------------
 * Requests use the path prefix `/api/...` (e.g., `/api/students`).
 * Vite's dev server proxy rewrites `/api` → `http://localhost:8000` before
 * forwarding the request to FastAPI.  This avoids a CORS preflight in the
 * browser during development because both the React page and the API request
 * now appear to share the same origin (http://localhost:5173).
 *
 * The proxy only exists in the dev server.  In production, a reverse proxy
 * (Nginx, Caddy, etc.) performs the same path-rewriting role.
 *
 * API Contract (Exercise 2):
 * ---------------------------
 * GET /students returns a JSON array:
 *   [
 *     { "id": 1, "name": "Mayank Acharya", "age": 28, "city": "Gandhinagar", "email": "..." },
 *     ...
 *   ]
 * The backend Student_response_model includes `is_active`, which is passed
 * through to the status badge and summary components.
 */

// ---------------------------------------------------------------------------
// GET /students — fetch all students
// ---------------------------------------------------------------------------

/**
 * Fetches the full student list from the FastAPI backend.
 *
 * Throws an Error (with the HTTP status code in the message) if the response
 * is not OK (2xx).  The caller is responsible for catching the error and
 * updating UI state accordingly (see App.jsx useEffect).
 *
 * @returns {Promise<Array>} Resolves with an array of student objects.
 * @throws  {Error}         Rejects when the HTTP status is not 2xx.
 */
export async function getStudents() {
  // /api/students is intercepted by the Vite proxy in dev and forwarded to
  // http://localhost:8000/students — no CORS preflight needed in the browser.
  const response = await fetch("/api/students");

  if (!response.ok) {
    // Include the status code so the error message is actionable during debug
    throw new Error(`Failed to fetch students: HTTP ${response.status}`);
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// GET /students/{id} — fetch one student by ID
// ---------------------------------------------------------------------------

/**
 * Fetches a single student record by their database ID.
 *
 * @param {number} id  The student's database primary key.
 * @returns {Promise<Object>} Resolves with a single student object.
 * @throws  {Error}          Rejects when the HTTP status is not 2xx.
 */
export async function getStudentById(id) {
  const response = await fetch(`/api/students/${id}`);

  if (!response.ok) {
    throw new Error(`Failed to fetch student ${id}: HTTP ${response.status}`);
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// POST /students/ — create a new student (Day 038 Exercise 7)
// ---------------------------------------------------------------------------

/**
 * Creates a new student record on the FastAPI backend.
 *
 * Day 038 Exercise 7: Submit to FastAPI
 *
 * Sends an HTTP POST request to /api/students/ (rewritten by Vite dev proxy
 * to http://localhost:8000/students/).
 *
 * Architecture flow:
 *   AddStudentForm → createStudent() → POST /api/students/ → Vite proxy
 *   → FastAPI router → Pydantic validation → StudentService → Repository → DB
 *
 * @param {Object} student - Payload containing { name, age, city, email, is_active }
 * @returns {Promise<Object>} The persisted student record returned by the server,
 *                            including the auto-generated `id`.
 * @throws {Error} If HTTP response status is not 2xx, parsed with server error details if available.
 */
export async function createStudent(student) {
  const response = await fetch("/api/students/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(student),
  });

  if (!response.ok) {
    let errorDetail = `HTTP ${response.status}`;
    try {
      const errorData = await response.json();
      if (errorData) {
        if (typeof errorData.detail === "string") {
          errorDetail = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          // FastAPI / Pydantic validation error format: [{loc: [...], msg: "...", type: "..."}]
          errorDetail = errorData.detail
            .map((err) => `${err.loc?.slice(1).join(".") || "field"}: ${err.msg}`)
            .join("; ");
        } else if (errorData.message) {
          errorDetail = errorData.message;
        }
      }
    } catch {
      // If response body is not JSON (e.g. gateway error HTML), retain status code
    }
    throw new Error(`Failed to create student: ${errorDetail}`);
  }

  return response.json();
}

