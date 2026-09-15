# React and Vite Exercises

## Exercise 1: Verify Node.js

Run:

```bash
node --version
```

Then:

```bash
npm --version
```

Current Vite requires Node.js `20.19+` or `22.12+` according to its current documentation.

If your installed Node version is below the current requirement, fix the environment before proceeding.

## Exercise 2: Scaffold the React Project

Use Vite:

```bash
npm create vite@latest student-management-ui
```

Choose:

- **Framework:** React
- **Variant:** JavaScript

We're intentionally using JavaScript for the first React week because your existing contract specifies React fundamentals, and your baseline already includes JavaScript/React experience.

Then:

```bash
cd student-management-ui
npm install
npm run dev
```

Vite serves the development app through its dev server; the current guide documents the default workflow and CLI.

## Exercise 3: Understand the Generated Project

Do not immediately delete everything.

Inspect:

```text
student-management-ui/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   └── ...
├── public/
├── index.html
├── package.json
└── vite.config.*
```

Your job is simply to answer:

1. What starts the application?
2. Where is `App` mounted?
3. Where is the root DOM node?
4. Where does Vite enter the project?

This is important because we don't want to blindly copy boilerplate.

## Exercise 4: Build the First Component Tree

Replace the default demo with:

```text
App
├── Header
├── StudentSummary
├── StudentList
│   └── StudentCard
└── Footer
```

Create:

```text
src/
├── components/
│   ├── Header.jsx
│   ├── StudentSummary.jsx
│   ├── StudentList.jsx
│   ├── StudentCard.jsx
│   └── Footer.jsx
├── App.jsx
└── main.jsx
```

Don't overengineer it.

Today's objective is understanding component composition.

## Exercise 5: Create Mock Student Data

Until Day 37+ when API integration becomes the focus, use local mock data.

Example:

```javascript
const students = [
  {
    id: 1,
    name: "Mayank Acharya",
    age: 28,
    city: "Gandhinagar",
    email: "mayank@example.com",
  },
  {
    id: 2,
    name: "Rahul Sharma",
    age: 25,
    city: "Ahmedabad",
    email: "rahul@example.com",
  },
  {
    id: 3,
    name: "Priya Patel",
    age: 24,
    city: "Mumbai",
    email: "priya@example.com",
  },
];
```

Then pass the list:

```text
App
↓
StudentList
↓
StudentCard
```

using props.

## Exercise 6: StudentCard

Exercise 6 — StudentCard

Create:

```jsx

  return (
    <article>
      <h2>{student.name}</h2>
      <p>Age: {student.age}</p>
      <p>City: {student.city}</p>
      <p>Email: {student.email}</p>
    </article>
  );
);
```

}

Then:

```jsx

  <StudentCard
<StudentCard
    key={student.id}
    student={student}
));
```

))

This exercise is deliberately connecting:

```text
Backend model
↓
JSON object shape
↓
React props
↓
Component
```

## Exercise 7: Conditional Rendering

Exercise 7 — Conditional Rendering

Add:
`Active` / `Inactive`
Active / Inactive

to your mock student model:

```javascript

  id: 1,
  name: "Mayank Acharya",
  active: true,
active: true
```

}

Then render:

```jsx

  ? <span>Active</span>
  : <span>Inactive</span>}
```

: <span>Inactive</span>
You're now combining:

- Props
- Conditional rendering

## Exercise 8: Student Selection with State

- Conditional rendering
  Exercise 8 — Student Selection with State

Now introduce your first meaningful state.

```jsx
In App.jsx:
```

const [selectedStudentId, setSelectedStudentId] = useState(null);

```text
When a student card is clicked:

StudentCard
↓
onSelect(student.id)
↓
App
↓
setSelectedStudentId(id)
```

Then display:

```text
Selected Student:
Mayank Acharya
```

This gives you the fundamental React loop:

```text
User interaction
↓
Event
↓
State update
↓
Re-render
↓
UI changes
```

That loop is more important today than memorizing useState syntax.

## Exercise 9: Add a Simple Student Summary

Create:

`StudentSummary`

and calculate:

- Total students
- Active students
- Inactive students

Example:

```text
Students

Total: 3
Active: 2
Inactive: 1
```

This forces you to combine:

- JavaScript arrays
- `map`/`filter`/`reduce` or equivalent logic
- React rendering

This is intentional because frontend engineering is still programming—not just HTML.

## Exercise 10: Build a Clean First Screen

Your screen should roughly contain:

```text
┌─────────────────────────────────────────────┐
│ Student Management System │
├─────────────────────────────────────────────┤
│ Total: 3 Active: 2 Inactive: 1 │
├─────────────────────────────────────────────┤
│ Student List │
│ │
│ ┌─────────────────────────────────────────┐ │
│ │ Mayank Acharya │ │
│ │ Age: 28 │ │
│ │ Gandhinagar │ │
│ │ mayank@example.com │ │
│ │ ● Active │ │
│ └─────────────────────────────────────────┘ │
│ │
│ ┌─────────────────────────────────────────┐ │
│ │ Rahul Sharma │ │
│ │ ... │ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ Selected: Mayank Acharya │
└─────────────────────────────────────────────┘
```

Don't spend 45 minutes on CSS.

Today is about React, not visual design.

## Exercise 11: React Debugging Drill

Deliberately introduce:

```jsx
key={student.name}
```

instead of:

```jsx
key={student.id}
```

Then think:

> Why is a stable database ID preferable to an arbitrary display value?

This reinforces the connection between backend identity and frontend rendering.

Then restore:

```jsx
key={student.id}
```
