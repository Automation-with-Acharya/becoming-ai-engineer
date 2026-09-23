/**
 * StudentCard.jsx
 *
 * Day 036 Exercises (unchanged):
 *   Exercise 6:  Renders a single student record inside <article>
 *   Exercise 7:  Conditional rendering — Active/Inactive badge
 *   Exercise 8:  onSelect callback prop — lifts selected ID to App
 *   Exercise 11: key={student.id} — use stable DB primary key, not name
 *
 * Day 037 Exercise 9: Presentation layer unchanged
 *   The component receives the same shape from the live API as it did
 *   from the mock data.  This is the payoff from building a clean
 *   component boundary in Day 036.
 *
 *   Previous flow:  mockStudents  → StudentList → StudentCard
 *   Current flow:   FastAPI JSON  → students state → StudentList → StudentCard
 *
 * Day 037 API contract note (Exercise 2):
 *   The API contract exposes `is_active`, matching the PostgreSQL column and
 *   Student_response_model field.
 *
 * Props:
 *   student   {Object}   — one student object
 *                          shape from API: { id, name, age, city, email, is_active }
 *   onSelect  {Function} — callback fired when card is clicked;
 *                          passes student.id up to App
 *
 * Exercise 11 note — about `key` props:
 *   The `key` used on this component when rendered in a list MUST be
 *   `student.id` (a stable database primary key), NOT `student.name`
 *   (a mutable display value). If two students share the same name, or
 *   a name changes, React would incorrectly reuse/reorder DOM nodes.
 *   Database IDs are guaranteed unique and stable — they are the right
 *   identity for reconciliation.
 *
 * Usage (in StudentList.jsx):
 *   <StudentCard key={student.id} student={student} onSelect={onSelect} />
 *   // ✅ Correct:  key={student.id}
 *   // ❌ Wrong:    key={student.name}  — see Exercise 11
 */

function StudentCard({ student, onSelect }) {
  return (
    // Semantic <article> — each card is a self-contained student record
    <article
      className="student-card"
      onClick={() => onSelect(student.id)}   // Exercise 8: lift state up
      role="button"                          // Accessibility: announce clickability
      tabIndex={0}                           // Keyboard-focusable
      onKeyDown={(e) => e.key === "Enter" && onSelect(student.id)} // Keyboard support
      aria-label={`Select student ${student.name}`}
    >
      <h2>{student.name}</h2>
      <p>Age: {student.age}</p>
      <p>City: {student.city}</p>
      <p>Email: {student.email}</p>

      {/*
        Exercise 7 (Day036): Conditional rendering — Active/Inactive badge.
        Exercise 9 (Day037): The status comes from the API's `is_active` field.
      */}
      <p className="status-badge">
        {student.is_active === true && (
          <span className="badge badge--active">✅ Active</span>
        )}
        {student.is_active === false && (
          <span className="badge badge--inactive">❌ Inactive</span>
        )}
        {student.is_active === undefined && (
          <span className="badge badge--unknown">— Status N/A</span>
        )}
      </p>
    </article>
  );
}

export default StudentCard;
