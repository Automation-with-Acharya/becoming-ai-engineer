# Day 036 — React Fundamentals: Components, JSX, Props & Component Thinking

> **Project ₹50L | 365-Day Career Transformation**  
> **Date:** 13 September 2026  
> **Week:** 6 — React Fundamentals & Frontend Engineering  
> **Phase:** 1 — Foundation & Build  
> **Primary Project:** Student Management System

---

# Learning Objectives

By the end of Day 36, you should be able to:

- Explain what React is solving in a modern web application.
- Think of a UI as a tree of reusable components rather than one large page.
- Create functional React components and compose them together.
- Read and write JSX confidently.
- Use JavaScript expressions inside JSX with `{}`.
- Pass data from parent components to child components using props.
- Use `children` for composition.
- Render content conditionally with normal JavaScript.
- Render arrays with `map()` and use stable `key` values.
- Attach event handlers such as `onClick`.
- Use `useState` for small pieces of interactive UI state.
- Understand the difference between props and state.
- Scaffold and run a React application with Vite.
- Map React components to the Student Management System frontend architecture.
- Apply simple array/hash-map DSA thinking while writing frontend logic.

---

# 1. Why Does React Exist?

A backend API can expose excellent business logic, validation, security, and database access and still leave the user with a poor experience if the browser UI is difficult to maintain.

A modern enterprise frontend needs to handle:

- reusable UI
- changing data
- user interactions
- conditional states
- lists of records
- forms
- API responses
- loading and error states
- clear separation of responsibilities

React provides a component-oriented model for building that UI.

The important mental shift is:

```text
Traditional mindset
-------------------
"Build one page and add more JavaScript to it."

React mindset
-------------
"Break the UI into reusable components whose output depends on data and state."
```

React's official documentation describes components as pieces of UI with their own logic and appearance, and presents applications as combinations of reusable, nestable components. citeturn667062search1turn667062search4

---

# 2. The Big Picture — Our Full-Stack Architecture

Day 36 starts the frontend half of the system we have already been building.

```text
                         USER / BROWSER
                               │
                               ▼
                    ┌─────────────────────┐
                    │      React UI       │
                    │                     │
                    │ App                 │
                    │ ├── Header          │
                    │ ├── StudentSummary  │
                    │ ├── StudentList     │
                    │ │    └── StudentCard│
                    │ └── Footer          │
                    │                     │
                    │ Props + State       │
                    │ Events + JSX        │
                    └──────────┬──────────┘
                               │
                          HTTP / JSON
                               │
                               ▼
                    ┌─────────────────────┐
                    │     FastAPI API     │
                    │                     │
                    │ Router              │
                    │   ↓                 │
                    │ Service             │
                    │   ↓                 │
                    │ Repository          │
                    │   ↓                 │
                    │ PostgreSQL          │
                    └─────────────────────┘
```

This is an important milestone in Project ₹50L:

> We are no longer learning a backend in isolation. We are starting to connect a maintainable frontend to the backend architecture already built.

---

# 3. React's Core Mental Model

Think of a React application as a **tree of components**.

```text
App
│
├── Header
│
├── StudentSummary
│
├── StudentList
│   │
│   ├── StudentCard
│   ├── StudentCard
│   └── StudentCard
│
└── Footer
```

Each component has a focused responsibility.

For example:

```text
App
└── owns page composition

Header
└── owns top-level navigation / branding

StudentSummary
└── owns counts / high-level student metrics

StudentList
└── owns list rendering

StudentCard
└── owns the presentation of one student

Footer
└── owns footer content
```

This decomposition is not about making the codebase contain as many files as possible. It is about choosing meaningful boundaries.

A useful rule:

> A component should have a reason to change.

If a student card changes because student display requirements changed, it should not require modifying the application's entire page component.

---

# 4. Your First React Component

A React component is typically a JavaScript function that returns UI markup.

```jsx
function StudentCard() {
  return (
    <article>
      <h2>Rahul Sharma</h2>
      <p>Python Engineering</p>
    </article>
  );
}
```

It can then be composed into another component:

```jsx
function App() {
  return (
    <main>
      <h1>Student Management System</h1>
      <StudentCard />
    </main>
  );
}
```

## Important rule

React component names begin with an uppercase letter:

```jsx
<StudentCard />
```

HTML elements use lowercase names:

```jsx
<section />
<div />
<button />
```

This naming convention lets React distinguish custom components from native HTML elements. citeturn667062search1

---

# 5. JSX — JavaScript + Markup

JSX is the markup syntax commonly used with React.

```jsx
const name = "Mayank";

function Welcome() {
  return <h1>Hello, {name}</h1>;
}
```

The `{}` means:

> Evaluate this JavaScript expression here.

Examples:

```jsx
const student = {
  name: "Aarav",
  age: 21,
};

function StudentInfo() {
  return (
    <section>
      <h2>{student.name}</h2>
      <p>Age: {student.age}</p>
    </section>
  );
}
```

## JSX is not HTML

There are several syntax differences.

### `className` instead of `class`

```jsx
<div className="student-card">
```

### Close tags properly

```jsx
<br />
<img src="avatar.png" alt="Student" />
```

### JavaScript expressions use `{}`

```jsx
<p>{student.name}</p>
```

React's Quick Start specifically covers JSX, styles, displaying data, conditions, lists, events, and state as core daily-use concepts. citeturn667062search1

---

# 6. JSX Expressions — Keep Rendering Close to the Data

JSX becomes powerful when the UI is a direct representation of application data.

```jsx
const student = {
  name: "Aarav",
  course: "Computer Science",
  age: 20,
};

function StudentCard() {
  return (
    <article>
      <h2>{student.name}</h2>
      <p>{student.course}</p>
      <p>Age: {student.age}</p>
    </article>
  );
}
```

The UI is now data-driven rather than hardcoded.

That distinction becomes critical once the data comes from FastAPI.

```text
FastAPI JSON
     │
     ▼
JavaScript object
     │
     ▼
React component
     │
     ▼
JSX
     │
     ▼
Browser UI
```

---

# 7. Props — Passing Data Into Components

**Props** are inputs passed from a parent component to a child component.

Example:

```jsx
function StudentCard({ name, course, age }) {
  return (
    <article>
      <h2>{name}</h2>
      <p>{course}</p>
      <p>Age: {age}</p>
    </article>
  );
}
```

Parent:

```jsx
function App() {
  return (
    <StudentCard
      name="Aarav"
      course="Computer Science"
      age={20}
    />
  );
}
```

Conceptually:

```text
             App
              │
       props ──┼──────────────┐
              │              │
              ▼              ▼
        StudentCard      StudentCard
```

The parent decides what data to provide.
The child decides how to display it.

This creates a clean separation:

```text
Parent
------
"Here is the data."

Child
-----
"Here is how I render that data."
```

React's documentation uses props as the mechanism for passing information down the component tree. citeturn667062search1turn667062search7

---

# 8. `children` — Composition Over Hardcoding

React also supports passing nested content through the special `children` prop.

```jsx
function Card({ children }) {
  return (
    <div className="card">
      {children}
    </div>
  );
}
```

Usage:

```jsx
<Card>
  <h2>Student Details</h2>
  <p>Aarav Sharma</p>
</Card>
```

The parent controls the inner content while `Card` controls the outer structure.

This is a foundation for reusable layout primitives.

```text
Card
├── border / spacing
├── layout rules
└── children
    ├── heading
    ├── text
    └── actions
```

This is an example of **composition**.

---

# 9. Props vs State

This distinction must become automatic.

| Concept | Props | State |
|---|---|---|
| Source | Parent component | Component / hook |
| Purpose | Pass data in | Remember changing data |
| Usually changes from | Parent | Event / state update |
| Child directly mutates it? | No | No; use state setter |
| Example | `student`, `onSelect` | `selectedStudentId`, `searchText` |

Mental model:

```text
Props
Parent ─────────────► Child
          data

State
Component ──► state setter ──► new render
```

Do not use state just because a value exists.
Use state when a changing value needs to affect what the component renders.

---

# 10. Conditional Rendering

React uses ordinary JavaScript for conditions.

## Ternary operator

```jsx
<p>
  {student.isActive ? "Active" : "Inactive"}
</p>
```

## Logical AND

```jsx
{student.isActive && <span>Active Student</span>}
```

## `if` before the return

```jsx
function StudentStatus({ isActive }) {
  let message;

  if (isActive) {
    message = "Active";
  } else {
    message = "Inactive";
  }

  return <p>{message}</p>;
}
```

Use the simplest form that remains readable.

React's official guidance explicitly shows `if`, `&&`, and `? :` as standard approaches to conditional rendering. citeturn667062search3

---

# 11. Rendering Lists

For the Student Management System, the list is central.

Data:

```jsx
const students = [
  { id: 101, name: "Aarav", course: "Python", isActive: true },
  { id: 102, name: "Diya", course: "React", isActive: true },
  { id: 103, name: "Rohan", course: "SQL", isActive: false },
];
```

Render:

```jsx
function StudentList({ students }) {
  return (
    <section>
      {students.map((student) => (
        <StudentCard
          key={student.id}
          student={student}
        />
      ))}
    </section>
  );
}
```

## Why the `key` matters

The `key` gives React a stable identity for each list item.

Use data-backed identity where possible:

```jsx
key={student.id}
```

Avoid relying on an array index when records have stable IDs and can be inserted, removed, or reordered.

React's documentation recommends stable keys that uniquely identify items among their siblings and notes that database IDs are a common source. citeturn667062search1

---

# 12. Event Handlers

React lets components respond to user interactions by passing handler functions to event props.

```jsx
function StudentCard() {
  function handleSelect() {
    console.log("Student selected");
  }

  return (
    <button onClick={handleSelect}>
      Select
    </button>
  );
}
```

Notice:

```jsx
onClick={handleSelect}
```

not:

```jsx
onClick={handleSelect()}
```

The first passes the function.
The second executes it during rendering.

This distinction is a common beginner bug and an important interview question.

---

# 13. State with `useState`

State stores information that changes over time and influences rendering.

```jsx
import { useState } from "react";

function StudentList() {
  const [selectedStudentId, setSelectedStudentId] = useState(null);

  function handleSelect(id) {
    setSelectedStudentId(id);
  }

  return (
    <button onClick={() => handleSelect(101)}>
      Select Student 101
    </button>
  );
}
```

The pattern is:

```text
const [value, setValue] = useState(initialValue)
```

Here:

```text
selectedStudentId
        │
        ├── current value
        │
        └── changes through setSelectedStudentId(...)
```

State changes cause React to render the UI again so the output reflects the new state. React's current interactivity documentation describes state as information that changes over time and explains that event handlers can update it. citeturn667062search9turn667062search1

---

# 14. The Student Management UI We Built

The first Day 36 frontend is intentionally small.

```text
App
│
├── Header
│
├── StudentSummary
│
├── StudentList
│   └── StudentCard × N
│
└── Footer
```

## App

Responsible for page composition and high-level state.

## Header

Responsible for application title / top-level branding.

## StudentSummary

Responsible for aggregated information such as:

- total students
- active students
- inactive students

## StudentList

Responsible for rendering a collection of students.

## StudentCard

Responsible for one student's presentation.

Example conceptual data flow:

```text
students[]
   │
   ▼
 App
   │
   ├────────────► StudentSummary
   │
   └────────────► StudentList
                     │
                     ├── student #101 ──► StudentCard
                     ├── student #102 ──► StudentCard
                     └── student #103 ──► StudentCard
```

---

# 15. Suggested Student Data Shape

Use a shape close to what the FastAPI backend will eventually return.

```js
const students = [
  {
    id: 101,
    name: "Aarav Sharma",
    age: 20,
    course: "Computer Science",
    isActive: true,
  },
  {
    id: 102,
    name: "Diya Patel",
    age: 21,
    course: "Data Science",
    isActive: true,
  },
  {
    id: 103,
    name: "Rohan Mehta",
    age: 22,
    course: "Software Engineering",
    isActive: false,
  },
];
```

This prepares the frontend for the eventual API contract.

---

# 16. Recommended Component Design

A clean version might look like this:

```text
src/
├── components/
│   ├── Header.jsx
│   ├── Footer.jsx
│   ├── StudentSummary.jsx
│   ├── StudentList.jsx
│   └── StudentCard.jsx
│
├── App.jsx
├── main.jsx
└── index.css
```

At this stage, avoid creating folders such as:

```text
utils/
services/
hooks/
contexts/
providers/
state/
```

unless the project actually needs them.

We are building architecture from real requirements, not from a checklist of fashionable folders.

---

# 17. Vite — React Project Setup

Vite provides the local development/build tooling around the React application.

Current official Vite guidance uses:

```bash
npm create vite@latest
```

and supports React templates. The current guide lists Node.js 20.19+ or 22.12+ as the baseline versions for Vite itself. citeturn667062search0

Example project setup:

```bash
npm create vite@latest student-management-ui
```

Choose:

```text
Framework: React
Variant: JavaScript
```

Then:

```bash
cd student-management-ui
npm install
npm run dev
```

Typical flow:

```text
Vite dev server
      │
      ▼
React source files
      │
      ▼
Browser
      │
      ▼
Fast feedback / HMR
```

Vite's official documentation describes its development server and fast HMR as core parts of the local development experience. citeturn667062search0turn667062search5

---

# 18. Day 36 Hands-On Exercise Pattern

The hands-on sequence should follow the same engineering principle used on the backend: build a thin vertical slice rather than writing a large amount of disconnected code.

## Step 1 — Scaffold

Create the Vite React project.

## Step 2 — Inspect

Understand:

- `package.json`
- `src/main.jsx`
- `src/App.jsx`
- CSS entry points
- dev/build scripts

## Step 3 — Decompose

Create the initial component tree.

## Step 4 — Add mock data

Use a small student array.

## Step 5 — Pass props

Send a student object from `StudentList` to `StudentCard`.

## Step 6 — Conditional UI

Show `Active` / `Inactive` based on `isActive`.

## Step 7 — Add interaction

Track selected student state.

## Step 8 — Validate list identity

Use `student.id` as the key.

## Step 9 — Clean up

Keep responsibilities clear and avoid premature abstractions.

---

# 19. Architecture Comparison — React vs ASP.NET Core / Enterprise Frontends

You already have enterprise experience with backend architecture, so use familiar patterns to reason about the frontend.

| Enterprise idea | React equivalent / mindset |
|---|---|
| Controller endpoint | UI event / route-level component boundary |
| DTO | Plain JS object / API response shape |
| Service layer | Business-oriented frontend logic/services when required |
| Dependency injection | React composition, props, hooks, context, and external DI patterns where justified |
| View / Razor component | React component + JSX |
| Model binding | Controlled inputs and explicit state/data flow |
| Partial view / reusable UI | Reusable React component |
| Request pipeline | Browser event → handler → state update → render |
| Configuration | Build/runtime environment configuration |

The comparison is conceptual, not one-to-one.

React does not automatically impose the same layered structure as an ASP.NET Core application. That is an advantage and a responsibility: the team must choose sensible boundaries.

---

# 20. Unidirectional Data Flow

A useful mental model is:

```text
         Parent State
              │
              ▼
            Props
              │
              ▼
           Child UI
              │
              ▼
          User Event
              │
              ▼
       Parent Handler
              │
              ▼
        State Update
              │
              ▼
         New Render
```

This makes the application easier to reason about than arbitrary two-way mutation.

For Student Management:

```text
selectedStudentId
       │
       ▼
     App
       │ props
       ▼
 StudentList
       │ props
       ▼
 StudentCard
       │
   click event
       │
       ▼
 App handler
       │
       ▼
setSelectedStudentId(...)
```

This becomes increasingly important as the UI grows.

---

# 21. Common Mistakes to Avoid

## Mistake 1 — Giant `App.jsx`

Everything works but becomes hard to understand.

**Fix:** extract components around real responsibilities.

## Mistake 2 — Treating props as mutable state

Do not try to mutate a prop directly.

```js
// Bad mental model
student.name = "New Name";
```

Instead, update the actual source of truth.

## Mistake 3 — Using array index as a key without thinking

```jsx
students.map((student, index) => (
  <StudentCard key={index} student={student} />
))
```

A stable record identifier is usually better when available.

## Mistake 4 — Calling event handlers while rendering

```jsx
// Wrong
onClick={handleDelete()}
```

Use:

```jsx
// Correct
onClick={handleDelete}
```

or, when arguments are required:

```jsx
onClick={() => handleDelete(student.id)}
```

## Mistake 5 — Putting every value into state

Derived values often do not need separate state.

For example:

```js
const activeStudents = students.filter(
  (student) => student.isActive
).length;
```

This can be derived from `students` rather than maintained as another independent state value.

## Mistake 6 — Premature architecture

Do not introduce global state, custom hooks, context providers, or elaborate service abstractions before the use case requires them.

---

# 22. Engineering Sprinkle — Component Boundaries Are Architecture

A practical engineering lesson from today's work:

> Frontend architecture is mostly about controlling change.

Suppose 6 developers work on a large dashboard.

Poor boundary:

```text
App.jsx
└── 1,700 lines of everything
```

Healthy boundary:

```text
App
├── Header
├── Navigation
├── Summary
├── Search
├── StudentList
├── StudentCard
├── Pagination
└── Footer
```

The second structure is not automatically “better” just because it has more files.
It is better when the boundaries match responsibility and team change patterns.

Think like a senior engineer:

```text
Component boundary
       ↓
Ownership boundary
       ↓
Change boundary
       ↓
Testing boundary
       ↓
Potential reuse boundary
```

This is the frontend equivalent of the repository/service boundaries you already built in the backend.

---

# 23. DSA Sprinkle — Arrays + Hashing in Frontend Thinking

Today’s DSA habit is intentionally small.

The frontend naturally produces array-processing problems, so practice the basic patterns while writing UI code.

## Pattern A — `map()`

Transform data:

```js
const names = students.map((student) => student.name);
```

Conceptually:

```text
students[]
   │
   ├── student 1 ──► name
   ├── student 2 ──► name
   └── student 3 ──► name
```

Time complexity:

```text
O(n)
```

## Pattern B — `Set` for duplicate detection

```js
const seen = new Set();

for (const value of values) {
  if (seen.has(value)) {
    return value;
  }
  seen.add(value);
}
```

Average lookup:

```text
O(1)
```

Overall:

```text
O(n)
```

## Two Sum mental model

Instead of checking every pair:

```text
O(n²)
```

use a hash map / object / `Map`:

```text
value → index
```

and reduce the expected search to:

```text
O(n)
```

The important takeaway for today is not “solve lots of LeetCode.”
It is:

> Recognize when a lookup structure turns repeated searching into near-constant-time lookup.

### Tiny practice set

1. **Two Sum** — understand the hash-map approach.
2. **Contains Duplicate** or **First Duplicate** — understand `Set`.

Keep the DSA portion small and focused on reasoning.

---

# 24. Interview Questions — Day 36

## React Fundamentals

### Q1. What is React?

A JavaScript library for building user interfaces using reusable components and declarative rendering.

### Q2. What is a component?

A reusable unit of UI that can contain its own rendering logic and behavior.

### Q3. What is JSX?

A syntax extension that lets JavaScript code express UI markup in a React-friendly form.

### Q4. Why do React component names start with uppercase letters?

To distinguish user-defined React components from native lowercase HTML elements.

### Q5. What are props?

Inputs passed from a parent component to a child component.

### Q6. What is state?

Data owned by a component that can change over time and affect what it renders.

### Q7. Props vs state?

Props are inputs from outside the component; state is internally managed changing data.

### Q8. Why are keys required in lists?

They provide stable identity so React can reason about list item changes such as insertion, deletion, and reordering.

### Q9. Why is `onClick={handleClick}` different from `onClick={handleClick()}`?

The first passes a function to be invoked later; the second invokes the function during rendering.

### Q10. What is `children`?

The prop used for content nested inside a component's opening and closing tags.

### Q11. Why should we avoid storing derived data in state?

Because duplicate sources of truth can become inconsistent; derivation from existing state/props is often simpler.

### Q12. What does `useState` return?

A state value and a setter function for updating that state.

---

# 25. Enterprise Interview Questions

### Q1. How would you structure a React application for an enterprise system?

Start with domain- and responsibility-based component boundaries, keep data flow predictable, isolate API/client concerns when they become non-trivial, and add shared state only where there is a real requirement.

### Q2. Where should API calls live?

The exact answer depends on the project architecture. Avoid placing every backend concern directly inside low-level presentational components. A growing application should establish a clear boundary between UI rendering and API/data access.

### Q3. How do you avoid prop drilling?

First question whether the state is actually shared broadly. For genuinely cross-cutting state, approaches such as Context or an external state library can be considered. Do not introduce them merely to avoid passing two or three props.

### Q4. How would you handle loading, error, and empty states?

Model them explicitly in the UI state rather than assuming every request ends in successful data.

### Q5. What does “component responsibility” mean in practice?

The component should own the rendering and behavior that belongs to its responsibility while avoiding unrelated business concerns.

---

# 26. Debugging Checklist

When a component does not behave correctly, inspect in this order:

```text
1. Is the component actually rendered?
        ↓
2. Are the props arriving?
        ↓
3. Is the JSX expression correct?
        ↓
4. Is the event handler attached correctly?
        ↓
5. Is state changing as expected?
        ↓
6. Is the list key stable?
        ↓
7. Is the source data correct?
```

Use browser developer tools and React-specific inspection tools when available, but first understand the data flow yourself.

---

# 27. Revision Cheat Sheet

```text
React
│
├── Component
│   └── reusable UI unit
│
├── JSX
│   └── UI syntax inside JavaScript
│
├── Props
│   └── parent → child data
│
├── children
│   └── composition
│
├── Conditional rendering
│   ├── if
│   ├── ? :
│   └── &&
│
├── Lists
│   ├── map()
│   └── stable key
│
├── Events
│   └── onClick={handler}
│
└── State
    └── useState()
```

---

# 28. Exact Learning Resources

## Primary Resource — React Quick Start

**URL:** https://react.dev/learn

### Stopping points for Day 36

Read these sections from the Quick Start page:

1. **Creating and nesting components**
2. **Writing markup with JSX**
3. **Adding styles**
4. **Displaying data**
5. **Conditional rendering**
6. **Rendering lists**
7. **Responding to events**
8. **Updating the screen**

These sections cover the React fundamentals used in the Day 36 build. citeturn667062search1

## React — Your First Component

**URL:** https://react.dev/learn/your-first-component

### Stopping point

Read the full page.

Focus on:

- what a component is
- defining a component
- using/nesting components

citeturn667062search4

## React — Describing the UI

**URL:** https://react.dev/learn/describing-the-ui

### Stopping point

Read through the sections covering:

- components
- multi-component files
- JSX
- curly braces
- props
- conditional rendering
- rendering multiple components
- keeping components pure
- thinking about UI as a tree

citeturn667062search7

## React — Conditional Rendering

**URL:** https://react.dev/learn/conditional-rendering

### Stopping point

Read the page fully enough to understand:

- `if`
- `&&`
- `? :`
- conditional inclusion/exclusion of JSX

citeturn667062search3

## React — Adding Interactivity

**URL:** https://react.dev/learn/adding-interactivity

### Stopping point

Read the sections on:

- responding to events
- state
- how React updates the UI

Do not go deeply into advanced state management yet; that belongs later in the roadmap. citeturn667062search9

## Vite — Getting Started

**URL:** https://vite.dev/guide/

### Stopping point

Read:

- Overview
- Scaffolding Your First Vite Project
- the `npm create vite@latest` flow
- Node.js compatibility note

citeturn667062search0

---

# 29. Day 36 Completion Standard

Day 36 is complete when you can do the following without copying a tutorial line-by-line:

```text
[ ] Create a React component.
[ ] Nest components.
[ ] Read/write basic JSX.
[ ] Display JavaScript data in JSX.
[ ] Pass props to a child component.
[ ] Use children for composition.
[ ] Render a condition.
[ ] Render a list with map().
[ ] Use a stable key.
[ ] Attach an event handler.
[ ] Create one small useState value.
[ ] Explain props vs state.
[ ] Explain the Student Management component tree.
[ ] Explain how the frontend will eventually call FastAPI.
[ ] Explain why component boundaries matter.
[ ] Solve the basic hash-map / Set DSA patterns conceptually.
```

---

# 30. What Comes Next

Day 36 establishes the frontend foundation.

The next major progression is to make the UI increasingly realistic:

```text
Day 36
React fundamentals
      ↓
Components / JSX / Props / State
      ↓
API integration
      ↓
Forms
      ↓
Student CRUD UI
      ↓
Authentication-aware UI
      ↓
Dashboard
      ↓
Full-stack Student Management System
```

The architecture we are building is deliberately incremental.

We already have:

```text
PostgreSQL
   ↑
Repository
   ↑
Service
   ↑
FastAPI
```

We are now adding:

```text
React
  ↓
HTTP / JSON
  ↓
FastAPI
```

That connection is the beginning of the full-stack system.

---

# Final Mental Model

Remember Day 36 as five ideas:

```text
1. Components
   Break UI into meaningful pieces.

2. JSX
   Describe what the UI should look like from JavaScript data.

3. Props
   Pass information from parent to child.

4. State
   Remember information that changes over time.

5. Composition
   Build bigger interfaces by combining smaller components.
```

And the senior-engineering perspective:

> **Good React code is not about writing JSX quickly. It is about designing clear UI boundaries and predictable data flow so the frontend can evolve without becoming a monolith.**

---

# Official References

- React Learn: https://react.dev/learn
- React — Your First Component: https://react.dev/learn/your-first-component
- React — Describing the UI: https://react.dev/learn/describing-the-ui
- React — Conditional Rendering: https://react.dev/learn/conditional-rendering
- React — Adding Interactivity: https://react.dev/learn/adding-interactivity
- Vite Getting Started: https://vite.dev/guide/

---

**Project ₹50L — Day 036 Complete**

**Core capability gained:** React component-oriented frontend engineering.  
**Next bridge:** React UI → FastAPI API integration.
