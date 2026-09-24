/**
 * Header.jsx
 *
 * Exercise 4: Component Tree — Header node
 *
 * Renders the top navigation bar / title banner for the Student Management
 * System.  Receives no props — it is a pure presentational component.
 *
 * Sits at the top of the component tree:
 *   App → Header
 */

function Header() {
  return (
    // Semantic <header> landmark element
    <header className="app-header">
      <h1>🎓 Student Management System</h1>
      <p className="header-subtitle">React + Vite + FastAPI — Day 038 Forms &amp; Input Validation</p>
    </header>
  );
}

export default Header;
