/**
 * App.jsx
 *
 * Day 038: React Forms & Input Validation
 *
 * Full-stack CRUD write-path integration:
 *   Exercise 1–11: Form component with controlled state, validation, submitting states,
 *                  server-error handling, API POST request, form reset, and list refresh.
 *   Exercise 12:   Complete CRUD write flow assembling AddStudentForm with StudentList.
 *
 * Day 037 exercises preserved:
 *   Exercise 3:  Uses studentApi.js as the HTTP boundary
 *   Exercise 4:  Replaces mockStudents.js with real API data via getStudents()
 *   Exercise 5:  Adds loading state — UI shows "Loading…" while request runs
 *   Exercise 6:  Adds error state — UI shows the actual error message
 *   Exercise 7:  useEffect fetches students on component mount
 *   Exercise 8:  Adds empty state — distinct from loading and error
 *   Exercise 9:  StudentList → StudentCard presentation layer is UNCHANGED
 *
 * Day 036 exercises preserved:
 *   Exercise 4:  Component tree — App → Header, AddStudentForm, Summary, List, Footer
 *   Exercise 8:  selectedStudentId state for card selection
 *
 * Data flow (Day 038 Complete Write-Read Cycle):
 *   User submits AddStudentForm
 *       ↓
 *   validateForm() (client validation: fast feedback)
 *       ↓
 *   createStudent(payload) → POST /api/students/ → FastAPI
 *       ↓
 *   Database persistence
 *       ↓
 *   loadStudents() → GET /api/students/
 *       ↓
 *   UI refreshes with updated student records
 */

import { useCallback, useEffect, useState } from "react";
import { getStudents } from "./api/studentApi";
import AddStudentForm from "./components/AddStudentForm";
import Footer from "./components/Footer";
import Header from "./components/Header";
import StudentList from "./components/StudentList";
import StudentSummary from "./components/StudentSummary";
import "./App.css";

function App() {
  // ─── Students + loading state ──────────────────────────────────────────
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);

  // ─── Error state ───────────────────────────────────────────────────────
  const [error, setError] = useState(null);

  // ─── Selected card state (Day 036) ─────────────────────────────────────
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  // ─── Fetch / Reload students function (Day 037 Ex 7 & Day 038 Ex 10) ───
  /**
   * Loads the latest student list from the backend API.
   * Defined with useCallback so it has a stable reference and can be
   * passed to AddStudentForm as onStudentAdded.
   */
  const loadStudents = useCallback(async () => {
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
  }, []);

  // Fetch students once on mount
  useEffect(() => {
    loadStudents();
  }, [loadStudents]);

  /**
   * Derive the selected student object from state.
   */
  const selectedStudent = students.find((s) => s.id === selectedStudentId);

  return (
    <>
      {/* Header landmark */}
      <Header />

      <main className="app-main">
        {/* ─── Day 038 Exercise 1 & 12: Add Student Form ───────────────────
            Form for creating new students. Sits above the list so users can
            enter data and immediately see the list update below upon submit. */}
        <AddStudentForm onStudentAdded={loadStudents} />

        {/* ─── Student Directory Section (Read View) ───────────────────── */}
        <section className="student-directory-section" aria-labelledby="directory-title">
          <h2 id="directory-title" className="visually-hidden">
            Registered Students Directory
          </h2>

          {/* Loading state indicator */}
          {loading && (
            <p className="status-message status-message--loading" aria-live="polite">
              ⏳ Loading students…
            </p>
          )}

          {/* Top-level fetch error indicator */}
          {error && (
            <p className="status-message status-message--error" role="alert">
              ❌ {error}
            </p>
          )}

          {/* Empty state indicator */}
          {!loading && !error && students.length === 0 && (
            <p className="status-message status-message--empty">
              📭 No students found. Use the form above to add the first student!
            </p>
          )}

          {/* Real data presentation */}
          {!loading && !error && students.length > 0 && (
            <>
              <StudentSummary students={students} />
              <StudentList students={students} onSelect={setSelectedStudentId} />
            </>
          )}
        </section>

        {/* Selected student banner */}
        {selectedStudent && (
          <section className="selected-section" aria-live="polite">
            <p>
              <strong>Selected Student:</strong> {selectedStudent.name} (ID: {selectedStudent.id}) &bull;{" "}
              {selectedStudent.city} &bull; {selectedStudent.email}
            </p>
          </section>
        )}
      </main>

      {/* Footer landmark */}
      <Footer />
    </>
  );
}

export default App;
