/**
 * App.jsx
 *
 * Exercise 3: Entry point analysis answers (see comments below)
 * Exercise 4: Root of the component tree
 *             App → Header, StudentSummary, StudentList → StudentCard, Footer
 * Exercise 5: Holds the mock student data; passes it down via props
 * Exercise 8: Introduces the first meaningful state — selectedStudentId
 *             The React loop demonstrated here:
 *               User clicks card → onSelect(id) → setSelectedStudentId(id)
 *               → state changes → re-render → "Selected: <name>" updates
 *
 * ---
 * Exercise 3 Answers:
 *   Q1. What starts the application?
 *       Vite's dev server (`npm run dev`) compiles and serves main.jsx.
 *
 *   Q2. Where is `App` mounted?
 *       In main.jsx — `createRoot(document.getElementById('root')).render(<App />)`
 *
 *   Q3. Where is the root DOM node?
 *       index.html — `<div id="root"></div>`
 *       Vite injects the <script type="module" src="/src/main.jsx"> tag,
 *       which bootstraps React and attaches the component tree to #root.
 *
 *   Q4. Where does Vite enter the project?
 *       vite.config.js — it scans for the `index.html` at the project root,
 *       which links to `src/main.jsx` as the module entry point.
 * ---
 */

import { useState } from "react";
import Footer from "./components/Footer";
import Header from "./components/Header";
import StudentList from "./components/StudentList";
import StudentSummary from "./components/StudentSummary";
import students from "./data/mockStudents";  // Exercise 5: local mock data
import "./App.css";

function App() {
  /**
   * Exercise 8: First meaningful piece of React state.
   *
   * selectedStudentId tracks which student card was last clicked.
   * null means "no selection yet."
   *
   * The React loop:
   *   1. User clicks a <StudentCard>
   *   2. StudentCard calls onSelect(student.id)
   *   3. App receives the id and calls setSelectedStudentId(id)
   *   4. State changes → React schedules a re-render
   *   5. On re-render, `selectedStudent` below resolves to the clicked student
   *   6. The "Selected Student" section updates in the UI
   */
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  /**
   * Derive the selected student object from state.
   * `Array.find` returns `undefined` when selectedStudentId is null,
   * which the JSX below handles with a conditional render.
   */
  const selectedStudent = students.find((s) => s.id === selectedStudentId);

  return (
    // React Fragment — avoids adding an extra DOM wrapper div
    <>
      {/* Exercise 4: Header sits at the top of the tree */}
      <Header />

      <main className="app-main">
        {/*
          Exercise 9: StudentSummary receives the full array so it can
          calculate total / active / inactive counts internally.
        */}
        <StudentSummary students={students} />

        {/*
          Exercise 5 & 8: StudentList receives both the data and the
          selection callback. It passes both down to each StudentCard.
        */}
        <StudentList
          students={students}
          onSelect={setSelectedStudentId}   // Exercise 8: lift state up
        />

        {/*
          Exercise 8: Display the selected student's name.
          Uses short-circuit (&&) to conditionally render only when a
          student has been selected.
        */}
        {selectedStudent && (
          <section className="selected-section" aria-live="polite">
            <p>
              <strong>Selected Student:</strong> {selectedStudent.name}
            </p>
          </section>
        )}
      </main>

      {/* Exercise 4: Footer sits at the bottom of the tree */}
      <Footer />
    </>
  );
}

export default App;
