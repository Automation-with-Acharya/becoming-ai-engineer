/**
 * mockStudents.js
 *
 * Exercise 5: Mock Student Data
 *
 * Provides a local in-memory array of student objects that mirrors the shape
 * returned by the FastAPI backend (Student_response_model).  This mock is used
 * until Day 37+ when the frontend switches to real API calls.
 *
 * Shape matches the backend JSON response:
 *   { id, name, age, city, email, active }
 *
 * The `active` field was added for Exercise 7 (conditional rendering).
 */

const students = [
  {
    id: 1,
    name: "Mayank Acharya",
    age: 28,
    city: "Gandhinagar",
    email: "mayank@example.com",
    active: true,    // Exercise 7: drives the Active/Inactive badge
  },
  {
    id: 2,
    name: "Rahul Sharma",
    age: 25,
    city: "Ahmedabad",
    email: "rahul@example.com",
    active: true,
  },
  {
    id: 3,
    name: "Priya Patel",
    age: 24,
    city: "Mumbai",
    email: "priya@example.com",
    active: false,   // Inactive student — renders the "Inactive" badge
  },
];

export default students;
