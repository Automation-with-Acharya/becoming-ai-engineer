/**
 * AddStudentForm.jsx
 *
 * Day 038: React Forms & Input Validation
 *
 * Implements the full CRUD write-path form for creating a new student:
 *
 * Exercises addressed in this file:
 *   Exercise 1:  AddStudentForm component containing Name, Age, City, Email, Active, Submit
 *   Exercise 2:  Controlled Fields — single form state object managed via useState
 *   Exercise 3:  Generic Change Handler — single handleChange handles text, number, email, checkbox
 *   Exercise 4:  Native HTML Validation — required, minLength, maxLength, min, type="email"
 *   Exercise 5:  React-Level Validation — validateForm function + errors state for business feedback
 *   Exercise 6:  Error Display — field-specific error messages + aria-invalid / aria-describedby
 *   Exercise 8:  Submitting State — submitting boolean disables button and shows "Creating..."
 *   Exercise 9:  Handle API Errors — submitError state displays server-side failures (400, 422, 500)
 *   Exercise 10: Refresh Student List — invokes onStudentAdded callback after successful POST
 *   Exercise 11: Reset Form — restores form to clean initial state on successful creation
 */

import { useState } from "react";
import { createStudent } from "../api/studentApi";

// ─── Initial Form State (Exercise 2 & 11) ──────────────────────────────────
// Kept outside component so resetForm can reference the exact default shape
const INITIAL_FORM_STATE = {
  name: "",
  age: "",
  city: "",
  email: "",
  is_active: true,
};

/**
 * Exercise 5: React-Level Validation Logic
 *
 * Validates the form state on the client before network transmission.
 * Fast feedback layer for friendly user experience without duplicating
 * every Pydantic/database constraint.
 *
 * @param {Object} formData - The current form values { name, age, city, email, is_active }
 * @returns {Object} An object mapping field names to error messages (empty if valid)
 */
function validateForm(formData) {
  const errors = {};

  // Name validation
  if (!formData.name.trim()) {
    errors.name = "Name is required.";
  } else if (formData.name.trim().length < 2) {
    errors.name = "Name must be at least 2 characters.";
  } else if (formData.name.trim().length > 100) {
    errors.name = "Name cannot exceed 100 characters.";
  }

  // Age validation
  if (formData.age === "" || formData.age === null || formData.age === undefined) {
    errors.age = "Age is required.";
  } else {
    const ageNum = Number(formData.age);
    if (Number.isNaN(ageNum)) {
      errors.age = "Age must be a valid number.";
    } else if (ageNum < 0) {
      errors.age = "Age cannot be negative.";
    } else if (!Number.isInteger(ageNum)) {
      errors.age = "Age must be a whole number.";
    }
  }

  // City validation
  if (!formData.city.trim()) {
    errors.city = "City is required.";
  } else if (formData.city.trim().length > 100) {
    errors.city = "City cannot exceed 100 characters.";
  }

  // Email validation (simple regex for client-side feedback)
  if (!formData.email.trim()) {
    errors.email = "Email is required.";
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
    errors.email = "Please enter a valid email address.";
  }

  return errors;
}

/**
 * AddStudentForm component.
 *
 * @param {Object} props
 * @param {Function} props.onStudentAdded - Callback invoked after a student is successfully created,
 *                                          enabling the parent (App) to reload the student list.
 */
function AddStudentForm({ onStudentAdded }) {
  // ─── Exercise 2: Controlled Form State ─────────────────────────────────
  const [form, setForm] = useState(INITIAL_FORM_STATE);

  // ─── Exercise 5: Validation Errors State ───────────────────────────────
  const [errors, setErrors] = useState({});

  // ─── Exercise 8: Submitting State ──────────────────────────────────────
  const [submitting, setSubmitting] = useState(false);

  // ─── Exercise 9: Server/API Error State ────────────────────────────────
  const [submitError, setSubmitError] = useState(null);

  // Success message state for visual confirmation
  const [successMessage, setSuccessMessage] = useState(null);

  // ─── Exercise 3: Generic Change Handler ────────────────────────────────
  /**
   * Single event handler that updates any form input.
   * Uses input `name` attribute to dynamically index the form state.
   * Handles checkboxes specially by reading `event.target.checked` instead of `value`.
   */
  function handleChange(event) {
    const { name, value, type, checked } = event.target;

    setForm((previous) => ({
      ...previous,
      [name]: type === "checkbox" ? checked : value,
    }));

    // Clear field-level error and general submit messages when user edits that field
    if (errors[name]) {
      setErrors((previous) => {
        const updated = { ...previous };
        delete updated[name];
        return updated;
      });
    }

    if (submitError) {
      setSubmitError(null);
    }
    if (successMessage) {
      setSuccessMessage(null);
    }
  }

  // ─── Form Submission Handler (Exercises 5, 7, 8, 9, 10, 11) ───────────
  async function handleSubmit(event) {
    // Prevent standard browser page reload on submit
    event.preventDefault();

    // Clear previous feedback
    setSubmitError(null);
    setSuccessMessage(null);

    // Exercise 5: Run client-side validation
    const validationErrors = validateForm(form);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return; // Stop submission on validation failure
    }

    // Prepare payload (convert age to integer for backend Pydantic model)
    const payload = {
      name: form.name.trim(),
      age: parseInt(form.age, 10),
      city: form.city.trim(),
      email: form.email.trim(),
      is_active: form.is_active,
    };

    // Exercise 8: Set submitting state while asynchronous API call runs
    try {
      setSubmitting(true);

      // Exercise 7: Call FastAPI backend via studentApi
      const createdStudent = await createStudent(payload);

      // Exercise 10: Refresh the parent student list
      if (typeof onStudentAdded === "function") {
        await onStudentAdded();
      }

      // Exercise 11: Reset form state on successful creation
      setForm(INITIAL_FORM_STATE);
      setErrors({});
      setSuccessMessage(`✅ Student "${createdStudent.name}" created successfully!`);
    } catch (error) {
      // Exercise 9: Catch and display server/API errors (400, 422, 500, etc.)
      setSubmitError(error.message);
    } finally {
      // Always reset submitting state regardless of outcome
      setSubmitting(false);
    }
  }

  return (
    <section className="add-student-section" aria-labelledby="add-student-title">
      <h2 id="add-student-title">Add New Student</h2>

      {/* Exercise 9: API Error Message */}
      {submitError && (
        <p className="form-submit-error" role="alert">
          ❌ {submitError}
        </p>
      )}

      {/* Submission Success Message */}
      {successMessage && (
        <p className="form-submit-success" role="status">
          {successMessage}
        </p>
      )}

      <form className="student-form" onSubmit={handleSubmit} noValidate>
        {/* Name Field (Exercises 4 & 6) */}
        <div className="form-group">
          <label htmlFor="student-name">
            Name <span className="required-indicator">*</span>
          </label>
          <input
            id="student-name"
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            placeholder="e.g. Alice Smith"
            required
            minLength={2}
            maxLength={100}
            aria-invalid={Boolean(errors.name)}
            aria-describedby={errors.name ? "name-error" : undefined}
          />
          {errors.name && (
            <p id="name-error" className="field-error">
              {errors.name}
            </p>
          )}
        </div>

        {/* Age Field (Exercises 4 & 6) */}
        <div className="form-group">
          <label htmlFor="student-age">
            Age <span className="required-indicator">*</span>
          </label>
          <input
            id="student-age"
            type="number"
            name="age"
            value={form.age}
            onChange={handleChange}
            placeholder="e.g. 21"
            required
            min={0}
            max={150}
            aria-invalid={Boolean(errors.age)}
            aria-describedby={errors.age ? "age-error" : undefined}
          />
          {errors.age && (
            <p id="age-error" className="field-error">
              {errors.age}
            </p>
          )}
        </div>

        {/* City Field (Exercises 4 & 6) */}
        <div className="form-group">
          <label htmlFor="student-city">
            City <span className="required-indicator">*</span>
          </label>
          <input
            id="student-city"
            type="text"
            name="city"
            value={form.city}
            onChange={handleChange}
            placeholder="e.g. Ahmedabad"
            required
            minLength={1}
            maxLength={100}
            aria-invalid={Boolean(errors.city)}
            aria-describedby={errors.city ? "city-error" : undefined}
          />
          {errors.city && (
            <p id="city-error" className="field-error">
              {errors.city}
            </p>
          )}
        </div>

        {/* Email Field (Exercises 4 & 6) */}
        <div className="form-group">
          <label htmlFor="student-email">
            Email <span className="required-indicator">*</span>
          </label>
          <input
            id="student-email"
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            placeholder="e.g. alice@example.com"
            required
            aria-invalid={Boolean(errors.email)}
            aria-describedby={errors.email ? "email-error" : undefined}
          />
          {errors.email && (
            <p id="email-error" className="field-error">
              {errors.email}
            </p>
          )}
        </div>

        {/* Active Checkbox (Exercises 1, 2, 3) */}
        <div className="form-group form-group--checkbox">
          <label htmlFor="student-is-active" className="checkbox-label">
            <input
              id="student-is-active"
              type="checkbox"
              name="is_active"
              checked={form.is_active}
              onChange={handleChange}
            />
            <span>Active Student</span>
          </label>
        </div>

        {/* Submit Button (Exercise 8) */}
        <div className="form-actions">
          <button type="submit" className="submit-button" disabled={submitting}>
            {submitting ? "⏳ Creating..." : "➕ Add Student"}
          </button>
        </div>
      </form>
    </section>
  );
}

export default AddStudentForm;
