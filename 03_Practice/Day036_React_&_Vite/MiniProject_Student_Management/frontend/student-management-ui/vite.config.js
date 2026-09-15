/**
 * vite.config.js
 *
 * Exercise 3: Where does Vite enter the project?
 *
 * Vite's configuration file.  When `npm run dev` is executed, Vite reads
 * this file first.  It then uses `index.html` (at the project root) as its
 * HTML entry point, which in turn links to `src/main.jsx`.
 *
 * `@vitejs/plugin-react` adds:
 *   - Babel-based JSX transform (converts JSX → React.createElement calls)
 *   - Fast Refresh (HMR that preserves component state on save)
 */

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(), // Enable React JSX transform + Fast Refresh
  ],
});
