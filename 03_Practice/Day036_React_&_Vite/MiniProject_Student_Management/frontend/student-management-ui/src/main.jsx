/**
 * main.jsx
 *
 * Exercise 3: Entry point analysis
 *
 * This file is the JavaScript entry point that Vite discovers through
 * the <script type="module" src="/src/main.jsx"> tag in index.html.
 *
 * What it does:
 *   1. Imports `StrictMode` — wraps the entire app in a double-render dev
 *      check that surfaces side-effects and deprecated APIs.
 *   2. Imports `createRoot` — the React 18+ concurrent-mode API that
 *      mounts the component tree onto a real DOM node.
 *   3. Finds `<div id="root">` from index.html and hands it to createRoot.
 *   4. Calls .render() to start React's reconciliation and paint the UI.
 *
 * This is the boundary between "plain HTML + browser" and "React land."
 * Everything below this line is managed by React's virtual DOM.
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";

// Mount the React application onto the #root div defined in index.html
createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
