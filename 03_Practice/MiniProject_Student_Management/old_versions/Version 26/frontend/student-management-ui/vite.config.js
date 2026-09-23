/**
 * vite.config.js
 *
 * Day 036 Exercise 3: Where does Vite enter the project?
 *   Vite's configuration file. When `npm run dev` is executed, Vite reads
 *   this file first. It then uses `index.html` at the project root as its
 *   HTML entry point, which links to `src/main.jsx`.
 *
 * Day 037 Exercise 11: Vite Development Proxy
 * -------------------------------------------
 * Problem this solves:
 *   React dev server runs on http://localhost:5173
 *   FastAPI backend runs on http://localhost:8000
 *   Normally a browser fetch() from origin :5173 to :8000 triggers a CORS
 *   preflight.  While CORS is configured on the backend, using a proxy keeps
 *   development simpler — no credentials or special headers needed for GETs.
 *
 * How the proxy works:
 *   Any request from React whose path starts with `/api` is intercepted by
 *   Vite's dev server and forwarded to http://localhost:8000.
 *   The `/api` prefix is stripped (rewrite rule) before the request reaches
 *   FastAPI, so `/api/students` → `http://localhost:8000/students`.
 *
 *   Browser (React)
 *       GET /api/students
 *            ↓
 *   Vite Dev Server (proxy)
 *       GET http://localhost:8000/students
 *            ↓
 *   FastAPI backend
 *
 * Does the proxy replace production CORS configuration?
 *   NO. The proxy only runs in the Vite dev server. In production, a real
 *   reverse proxy (Nginx, Caddy, etc.) or a same-origin deployment handles
 *   routing.  The CORS middleware on the FastAPI backend remains necessary
 *   for any deployment where the frontend and backend are on different origins.
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

  server: {
    // ── Exercise 11: Development proxy ────────────────────────────────────
    // Routes requests whose path starts with /api to the FastAPI backend.
    // The `rewrite` strips the /api prefix before forwarding.
    proxy: {
      "/api": {
        target: "http://localhost:8000",   // FastAPI backend address
        changeOrigin: true,                // Sets Host header to match target
        rewrite: (path) => path.replace(/^\/api/, ""),
        // /api/students  →  http://localhost:8000/students
        // /api/students/1 →  http://localhost:8000/students/1
      },
    },
  },
});
