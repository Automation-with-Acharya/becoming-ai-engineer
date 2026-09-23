/**
 * StudentList.jsx
 *
 * Exercise 4: Component Tree — StudentList node
 * Exercise 5: Receives the students array as a prop
 * Exercise 6: Maps each student to a <StudentCard>
 * Exercise 8: Forwards the onSelect callback down to StudentCard
 *
 * Props:
 *   students  {Array}    — full student array passed from App
 *   onSelect  {Function} — callback to lift the selected student ID to App
 *
 * Rendering strategy:
 *   Array.map() converts each student object into a <StudentCard> element.
 *   The `key` prop is set to `student.id` (stable DB primary key) — see
 *   Exercise 11 for why this matters.
 *
 * Component tree position:
 *   App → StudentList → StudentCard
 */

import StudentCard from "./StudentCard";

function StudentList({ students, onSelect }) {
  return (
    <section className="student-list" aria-label="Student list">
      <h2>Student List</h2>

      {/*
        Exercise 6 + 11:
        Map the array to <StudentCard> components.
        key={student.id}  → stable, unique DB primary key  ✅
        key={student.name} would be wrong (not unique, mutable) ❌
      */}
      <div className="cards-grid">
        {students.map((student) => (
          <StudentCard
            key={student.id}      // Exercise 11: always use the stable DB ID
            student={student}     // Exercise 5 & 6: pass the full object as prop
            onSelect={onSelect}   // Exercise 8: forward callback to StudentCard
          />
        ))}
      </div>
    </section>
  );
}

export default StudentList;
