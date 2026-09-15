/**
 * Footer.jsx
 *
 * Exercise 4: Component Tree — Footer node
 *
 * Renders the bottom footer for the application.
 * Pure presentational component; receives no props.
 *
 * Sits at the bottom of the component tree:
 *   App → Footer
 */

function Footer() {
  return (
    // Semantic <footer> landmark element
    <footer className="app-footer">
      <p>Day 036 — React &amp; Vite &nbsp;|&nbsp; Student Management Mini Project</p>
    </footer>
  );
}

export default Footer;
