/**
 * App.jsx
 *
 * Day 037: React ↔ FastAPI API Integration
 *
 * Exercises addressed in this file:
 *   Exercise 3:  Uses studentApi.js as the HTTP boundary (not inline fetch)
 *   Exercise 4:  Replaces mockStudents.js with real API data via getStudents()
 *   Exercise 5:  Adds loading state — UI shows "Loading…" while request runs
 *   Exercise 6:  Adds error state — UI shows the actual error message (dev-friendly)
 *   Exercise 7:  useEffect fetches students on component mount ([] dependency)
 *   Exercise 8:  Adds empty state — distinct from loading and error
 *   Exercise 9:  StudentList → StudentCard presentation layer is UNCHANGED
 *                (only the source of `students` data changed; components didn't)
 *
 * Day 036 exercises carried forward (comments preserved):
 *   Exercise 3 (Day036): Entry-point analysis (see main.jsx / vite.config.js)
 *   Exercise 4 (Day036): Component tree — App → Header, Summary, List, Footer
 *   Exercise 8 (Day036): selectedStudentId state for card selection
 *
 * State owned by App:
 *   students         {Array}       Live data from FastAPI (replaces mockStudents)
 *   loading          {boolean}     True while the API request is in-flight
 *   error            {string|null} Error message string if request failed
 *   selectedStudentId{number|null} ID of the clicked StudentCard (Day036 Ex8)
 *
 * Data flow (Day 037):
 *   FastAPI /students endpoint
 *       ↓  HTTP GET (via Vite proxy → http://localhost:8000)
 *   studentApi.getStudents()
 *       ↓  Promise resolves
 *   setStudents(data)
 *       ↓  React re-renders
 *   StudentSummary, StudentList, StudentCard
 */

import { useEffect, useState } from "react";
import { getStudents } from "./api/studentApi";   // Exercise 3: dedicated API module
import Footer from "./components/Footer";
import Header from "./components/Header";
import StudentList from "./components/StudentList";
import StudentSummary from "./components/StudentSummary";
import "./App.css";

// mockStudents import removed — Exercise 4: data now comes from FastAPI

function App() {
  // ─── Exercise 5: Students + loading state ───────────────────────────────
  // students starts as an empty array so map() is always safe even before load
  const [students, setStudents] = useState([]);

  // loading=true on mount; set to false after the request completes (success or fail)
  const [loading, setLoading] = useState(true);

  // ─── Exercise 6: Error state ─────────────────────────────────────────────
  // Holds the error message string from the caught Error object.
  // null means "no error yet."
  const [error, setError] = useState(null);

  // ─── Day 036 Exercise 8: selected card state ─────────────────────────────
  // null = nothing selected. Updated when user clicks a StudentCard.
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  // ─── Exercise 7: Fetch students on component mount ───────────────────────
  /**
   * useEffect with an empty dependency array [] runs exactly once:
   * after the first render (i.e., on mount).  This is where we kick off
   * the side-effect of fetching data from the network.
   *
   * Why an inner async function instead of making the effect itself async?
   * useEffect's callback must return either nothing or a cleanup function.
   * An async function returns a Promise, which React does not know how to
   * use as a cleanup.  The pattern is: define an async inner function and
   * call it immediately.
   *
   * The React lifecycle for this effect:
   *   App renders (loading=true, students=[])
   *       ↓
   *   useEffect fires (after paint)
   *       ↓
   *   loadStudents() → fetch /api/students
   *       ↓
   *   setStudents(data)   OR   setError(err.message)
   *       ↓
   *   setLoading(false)      ← always runs (finally block)
   *       ↓
   *   React re-renders with real data / error / empty state
   */
  useEffect(() => {
    async function loadStudents() {
      try {
        setLoading(true);   // Ensure loading=true at the start of every fetch attempt
        setError(null);     // Clear any previous error before retrying

        const data = await getStudents();  // Exercise 3: delegate HTTP to API module
        setStudents(data);
      } catch (err) {
        // Exercise 6: Preserve the actual error message for dev debugging
        setError(err.message);
      } finally {
        // finally always runs — clears the loading state regardless of success/fail
        setLoading(false);
      }
    }

    loadStudents();
  }, []); // [] = run once on mount only (no reactive dependencies)

  /**
   * Derive the selected student object from state.
   * When students arrive from the API, this find() will resolve correctly
   * because the IDs come directly from the database (same as the mock IDs did).
   */
  const selectedStudent = students.find((s) => s.id === selectedStudentId);

  return (
    // React Fragment — avoids adding an extra DOM wrapper div
    <>
      {/* Day 036 Exercise 4: Header sits at the top of the tree */}
      <Header />

      <main className="app-main">

        {/* ─── Exercise 5: Loading state ───────────────────────────────────
            Show a loading indicator while the API request is in-flight.
            "Loading" and "empty list" are different states — never conflate them. */}
        {loading && (
          <p className="status-message status-message--loading" aria-live="polite">
            ⏳ Loading students…
          </p>
        )}

        {/* ─── Exercise 6: Error state ─────────────────────────────────────
            Show the actual error message so developers can debug the
            browser-to-API boundary during development. */}
        {error && (
          <p className="status-message status-message--error" role="alert">
            ❌ {error}
          </p>
        )}

        {/* ─── Exercise 8: Empty state ─────────────────────────────────────
            Shown only after loading finishes, no error occurred, and the
            API returned zero students.  This must NOT appear while loading. */}
        {!loading && !error && students.length === 0 && (
          <p className="status-message status-message--empty">
            📭 No students found.
          </p>
        )}

        {/* ─── Exercises 4 & 9: Real data drives the same presentation layer.
            StudentSummary and StudentList are completely unchanged from Day 036 —
            only the source of the `students` array changed (API vs mock). */}
        {!loading && !error && students.length > 0 && (
          <>
            {/* Day 036 Exercise 9: StudentSummary derives stats from the array */}
            <StudentSummary students={students} />

            {/* Day 036 Exercise 5 & 8: StudentList passes data + selection callback */}
            <StudentList
              students={students}
              onSelect={setSelectedStudentId}
            />
          </>
        )}

        {/* Day 036 Exercise 8: Selected student banner — state-driven */}
        {selectedStudent && (
          <section className="selected-section" aria-live="polite">
            <p>
              <strong>Selected Student:</strong> {selectedStudent.name}
            </p>
          </section>
        )}
      </main>

      {/* Day 036 Exercise 4: Footer sits at the bottom of the tree */}
      <Footer />
    </>
  );
}

export default App;
