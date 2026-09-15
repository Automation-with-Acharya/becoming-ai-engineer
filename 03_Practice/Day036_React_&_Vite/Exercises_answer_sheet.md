# React & Vite — Exercises Answer Sheet

**Day:** 036  
**Date:** 2026-09-15  
**Project:** `MiniProject_Student_Management / frontend / student-management-ui`  
**Stack:** React 19 + Vite 8 + JavaScript (no TypeScript)

---

## Exercise 1: Verify Node.js

**Command run:**

```bash
node --version
npm --version
```

**Output:**

```
v22.22.3
10.9.8
```

**Verdict:** ✅ Node `22.22.3` satisfies Vite's `22.12+` requirement. No environment fix needed.

---

## Exercise 2: Scaffold the React Project

**Command already executed by user:**

```bash
npm create vite@latest student-management-ui
# Framework: React
# Variant: JavaScript
cd student-management-ui
npm install
npm run dev
```

**Result:** Vite scaffolded the project at  
`MiniProject_Student_Management/frontend/student-management-ui/`

**Observation:**  
Vite serves the dev app via its built-in dev server with HMR (Hot Module Replacement) — file saves update the browser instantly without a full page reload.

---

## Exercise 3: Understand the Generated Project

### Q1. What starts the application?

`npm run dev` → Vite dev server starts → reads `vite.config.js` → serves `index.html` as the entry point → the browser loads `src/main.jsx` as an ES module.

### Q2. Where is `App` mounted?

In **`src/main.jsx`**:

```jsx
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>
)
```

`App` is passed to `createRoot().render()`, which attaches the React component tree to the `#root` DOM node.

### Q3. Where is the root DOM node?

In **`index.html`**:

```html
<div id="root"></div>
```

This is the single empty `<div>` that React controls entirely. React replaces its contents with the virtual DOM tree.

### Q4. Where does Vite enter the project?

Vite's entry point is **`index.html`** at the project root — specifically the `<script type="module" src="/src/main.jsx">` tag inside it. Vite reads `vite.config.js` for plugin and build configuration, then crawls all `import` statements starting from `main.jsx`.

---

## Exercise 4: Build the First Component Tree

### Component tree structure built:

```
App
├── Header
├── StudentSummary
├── StudentList
│   └── StudentCard (×3 — one per student)
└── Footer
```

### Files created:

| File | Role |
|------|------|
| `src/components/Header.jsx` | App title bar |
| `src/components/Footer.jsx` | Bottom banner |
| `src/components/StudentSummary.jsx` | Stats: total / active / inactive |
| `src/components/StudentList.jsx` | Maps student array → StudentCard |
| `src/components/StudentCard.jsx` | Single student record |
| `src/App.jsx` | Root — owns state and wires all components |

**Key learning:** Component composition means each component has a single job. `App` only orchestrates — it does not render individual student fields itself.

---

## Exercise 5: Create Mock Student Data

**File created:** `src/data/mockStudents.js`

```javascript
const students = [
  { id: 1, name: "Mayank Acharya", age: 28, city: "Gandhinagar", email: "mayank@example.com", active: true },
  { id: 2, name: "Rahul Sharma",   age: 25, city: "Ahmedabad",   email: "rahul@example.com",  active: true },
  { id: 3, name: "Priya Patel",    age: 24, city: "Mumbai",      email: "priya@example.com",  active: false },
];
export default students;
```

**Data flow:**

```
App (imports mockStudents)
  ↓ props: students={students}
StudentList
  ↓ props: student={student}  (per .map iteration)
StudentCard
```

**Connection to backend:** The object shape (`id, name, age, city, email`) mirrors the `Student_response_model` returned by the FastAPI backend. When the real API is connected (Day 37+), the mock array will be replaced by the API response — no component changes needed.

---

## Exercise 6: StudentCard

**File:** `src/components/StudentCard.jsx`

```jsx
function StudentCard({ student, onSelect }) {
  return (
    <article onClick={() => onSelect(student.id)}>
      <h2>{student.name}</h2>
      <p>Age: {student.age}</p>
      <p>City: {student.city}</p>
      <p>Email: {student.email}</p>
    </article>
  );
}
```

**Chain demonstrated:**

```
Backend model (Student_response_model)
    ↓
JSON object shape { id, name, age, city, email }
    ↓
React props  { student }
    ↓
Component    <StudentCard student={student} />
```

---

## Exercise 7: Conditional Rendering

**Field added to mock data:** `active: true / false`

**JSX conditional in `StudentCard.jsx`:**

```jsx
{student.active
  ? <span className="badge badge--active">✅ Active</span>
  : <span className="badge badge--inactive">❌ Inactive</span>
}
```

**Concepts combined:**
- **Props** — `student` object passed in
- **Conditional rendering** — ternary operator evaluates `student.active` at render time

---

## Exercise 8: Student Selection with State

**State declared in `App.jsx`:**

```jsx
const [selectedStudentId, setSelectedStudentId] = useState(null);
```

**The React loop:**

```
1. User clicks StudentCard
2. onClick → onSelect(student.id)
3. App receives id → setSelectedStudentId(id)
4. State updates → React re-renders App
5. selectedStudent = students.find(s => s.id === selectedStudentId)
6. UI shows: "Selected Student: Mayank Acharya"
```

**Why this loop matters more than syntax:**  
React is fundamentally a UI = f(state) system. Memorising `useState` is easy; understanding that *any* user interaction must travel through a state update before the UI can change is the core mental model.

---

## Exercise 9: Add a Simple Student Summary

**File:** `src/components/StudentSummary.jsx`

```jsx
function StudentSummary({ students }) {
  const total    = students.length;
  const active   = students.filter((s) => s.active).length;
  const inactive = total - active;

  return (
    <section>
      <p>Total: {total}</p>
      <p>Active: {active}</p>
      <p>Inactive: {inactive}</p>
    </section>
  );
}
```

**Output rendered:**

```
Students

Total: 3   Active: 2   Inactive: 1
```

**Concepts combined:** JavaScript array methods (`filter`, `.length`) + React rendering. No state needed — these are pure derivations from the `students` prop.

---

## Exercise 10: Build a Clean First Screen

**Screen layout implemented:**

```
┌──────────────────────────────────────────────┐
│   🎓 Student Management System               │  ← Header
├──────────────────────────────────────────────┤
│  Total: 3  Active: 2  Inactive: 1            │  ← StudentSummary
├──────────────────────────────────────────────┤
│  Student List                                │  ← StudentList
│                                              │
│  ┌────────────────┐  ┌────────────────┐      │
│  │ Mayank Acharya │  │ Rahul Sharma   │      │
│  │ Age: 28        │  │ Age: 25        │      │  ← StudentCard ×3
│  │ Gandhinagar    │  │ Ahmedabad      │      │
│  │ ✅ Active      │  │ ✅ Active      │      │
│  └────────────────┘  └────────────────┘      │
│  ┌────────────────┐                          │
│  │ Priya Patel    │                          │
│  │ Age: 24        │                          │
│  │ Mumbai         │                          │
│  │ ❌ Inactive    │                          │
│  └────────────────┘                          │
├──────────────────────────────────────────────┤
│  Selected Student: Mayank Acharya            │  ← State banner (Exercise 8)
├──────────────────────────────────────────────┤
│  Day 036 — React & Vite | Mini Project      │  ← Footer
└──────────────────────────────────────────────┘
```

CSS kept minimal and functional per exercise instructions ("don't spend 45 minutes on CSS — today is about React").

---

## Exercise 11: React Debugging Drill

### The deliberate mistake:

```jsx
// ❌ Wrong — using student.name as key
<StudentCard key={student.name} student={student} onSelect={onSelect} />
```

### Why `key={student.name}` is wrong:

1. **Not guaranteed unique:** Two students could have the same name (e.g., two "Rahul Sharma"s). React would reuse the same DOM node for both → incorrect rendering, missed updates.

2. **Mutable display value:** A student's name can change. If the name changes, React treats the new key as a completely new component and unmounts/remounts — destroying local state and causing unnecessary re-renders.

3. **No connection to backend identity:** The `key` is React's internal reconciliation signal, not a display value. It should come from the same identity the server uses — the **primary key** (`id`).

### The correct fix (restored):

```jsx
// ✅ Correct — stable, unique DB primary key
<StudentCard key={student.id} student={student} onSelect={onSelect} />
```

### Backend ↔ Frontend identity connection:

```
Backend PRIMARY KEY (id)  →  stable, unique, immutable
     ↓
JSON response { id: 1, ... }
     ↓
React key={student.id}    →  stable reconciliation identity
```

The `key` prop is the place where the frontend explicitly acknowledges the backend's identity system.

---

## Files Summary

| File | Status | Exercise(s) |
|------|--------|-------------|
| `src/main.jsx` | Modified (comments) | 3 |
| `src/index.css` | Modified (reset + comments) | 10 |
| `src/App.jsx` | **Replaced** | 3, 4, 5, 8, 9, 10 |
| `src/App.css` | **Replaced** | 10 |
| `index.html` | Modified (comments + SEO) | 3 |
| `vite.config.js` | Modified (comments) | 3 |
| `src/data/mockStudents.js` | **New** | 5, 7 |
| `src/components/Header.jsx` | **New** | 4 |
| `src/components/Footer.jsx` | **New** | 4 |
| `src/components/StudentSummary.jsx` | **New** | 4, 9 |
| `src/components/StudentList.jsx` | **New** | 4, 5, 6, 8, 11 |
| `src/components/StudentCard.jsx` | **New** | 4, 6, 7, 8, 11 |
