/**
 * StudentCard.jsx
 *
 * Exercise 6: StudentCard Component
 * Exercise 7: Conditional Rendering (Active/Inactive badge)
 * Exercise 8: Student Selection (onSelect callback prop)
 * Exercise 11: Debugging Drill key prop note
 *
 * Renders a single student record inside a semantic <article> element.
 *
 * Props:
 *   student   {Object}   — one student object from the mock data array
 *                          shape: { id, name, age, city, email, active }
 *   onSelect  {Function} — callback fired when card is clicked;
 *                          passes student.id up to App (Exercise 8)
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
        Exercise 7: Conditional rendering
        Ternary operator renders either the "Active" or "Inactive" badge
        depending on the student.active boolean field.
      */}
      <p className="status-badge">
        {student.active
          ? <span className="badge badge--active">✅ Active</span>
          : <span className="badge badge--inactive">❌ Inactive</span>
        }
      </p>
    </article>
  );
}

export default StudentCard;
