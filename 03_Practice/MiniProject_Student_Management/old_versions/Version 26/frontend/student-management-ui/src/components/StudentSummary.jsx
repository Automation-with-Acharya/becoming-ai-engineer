/**
 * StudentSummary.jsx
 *
 * Exercise 9: Add a Simple Student Summary
 *
 * Receives the full `students` array as a prop and derives three stats:
 *   - Total students     (students.length)
 *   - Active students    (filter by student.is_active === true)
 *   - Inactive students  (filter by student.is_active === false)
 *
 * No state is needed — every value is a pure derivation from props.
 *
 * Component tree position:
 *   App → StudentSummary
 *
 * Props:
 *   students  {Array}  — the full mock/live student list from App
 */

function StudentSummary({ students }) {
  // Derive stats directly from the prop array (no useState needed here)
  const total    = students.length;
  const active   = students.filter((s) => s.is_active === true).length;
  const inactive = students.filter((s) => s.is_active === false).length;

  return (
    <section className="student-summary" aria-label="Student summary statistics">
      <h2>Students</h2>

      {/* Display each derived stat */}
      <div className="summary-stats">
        <span className="stat">
          <strong>Total:</strong> {total}
        </span>
        <span className="stat stat--active">
          <strong>Active:</strong> {active}
        </span>
        <span className="stat stat--inactive">
          <strong>Inactive:</strong> {inactive}
        </span>
      </div>
    </section>
  );
}

export default StudentSummary;
