/* ============================================================
   api.js — Central API helper + shared utility functions
   ============================================================
   This file is loaded by every page. It provides:
     1. apiRequest()   — A wrapper around fetch() for all API calls
     2. api object     — Shortcuts for GET, POST, PUT, DELETE
     3. Named functions for each feature (auth, tasks, habits, dashboard)
     4. Shared helpers: showToast(), escapeHtml(), formatDate()
        (Defined here once so tasks.js and habits.js don't repeat them)
   ============================================================ */

const API_BASE = "http://127.0.0.1:5000"; // Flask backend runs on port 5000

/**
 * Makes an HTTP request to the Flask backend.
 * Always sends/receives JSON. Includes session cookie (credentials: 'include').
 *
 * @param {string} method   - HTTP method: 'GET', 'POST', 'PUT', 'DELETE'
 * @param {string} endpoint - API path, e.g. '/tasks'
 * @param {object} body     - Optional JSON body (for POST/PUT requests)
 * @returns {{ ok: boolean, status: number, data: object }}
 */
async function apiRequest(method, endpoint, body = null) {
  const options = {
    method,
    credentials: "include", // Send the session cookie with every request
    headers: { "Content-Type": "application/json" }, // Tell Flask to parse the body as JSON
  };

  if (body) {
    options.body = JSON.stringify(body); // Convert JS object to JSON string
  }

  try {
    const response = await fetch(API_BASE + endpoint, options);
    const data = await response.json();
    return { ok: response.ok, status: response.status, data };
  } catch (err) {
    // Network error (e.g. Flask server is not running)
    return {
      ok: false,
      status: 0,
      data: {
        status: "error",
        message: "Server error ",
      },
    };
  }
}

// Shortcut methods so route files can write: api.get('/tasks') instead of apiRequest('GET', '/tasks')
const api = {
  get: (url) => apiRequest("GET", url),
  post: (url, body) => apiRequest("POST", url, body),
  put: (url, body) => apiRequest("PUT", url, body),
  delete: (url) => apiRequest("DELETE", url),
};

/* ── Auth functions ── */

async function authRegister(username, email, password) {
  return api.post("/register", { username, email, password });
}

async function authLogin(email, password) {
  const result = await api.post("/login", { email, password });
  // BUG FIX: Save username to localStorage on successful login
  // so the dashboard/tasks/habits pages can show the user's name
  if (result.ok && result.data.username) {
    localStorage.setItem("prodify-username", result.data.username);
  }
  return result;
}

async function authLogout() {
  return api.get("/logout");
}

/* ── Task functions ── */

async function fetchTasks() {
  return api.get("/tasks");
}

async function createTask(title, description) {
  return api.post("/tasks", { title, description });
}

async function completeTask(id) {
  return api.put(`/tasks/${id}`, { status: "completed" });
}

async function deleteTask(id) {
  return api.delete(`/tasks/${id}`);
}

/* ── Habit functions ── */

async function fetchHabits() {
  return api.get("/habits");
}

async function createHabit(habit_name) {
  return api.post("/habits", { habit_name });
}

async function completeHabit(habit_id) {
  return api.post("/habits/complete", { habit_id });
}

async function deleteHabit(id) {
  return api.delete(`/habits/${id}`);
}

/* ── Dashboard function ── */

async function fetchDashboardStats() {
  return api.get("/dashboard-stats");
}

/* ============================================================
   Shared Utility Functions
   These are defined here (not in tasks.js / habits.js) to
   avoid duplicating the same code in every file.
   ============================================================ */

/**
 * Shows a popup toast notification at the bottom of the screen.
 * Auto-dismisses after 3 seconds.
 *
 * @param {string} message - Text to display
 * @param {string} type    - 'success', 'error', or 'info'
 */
function showToast(message, type = "info") {
  // Find or create the toast container
  let container = document.querySelector(".toast-container");
  if (!container) {
    container = document.createElement("div");
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const icons = { success: "✅", error: "❌", info: "ℹ️" };

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <span class="toast-icon">${icons[type] || "ℹ️"}</span>
    <span class="toast-msg">${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);

  // Fade out and remove after 3 seconds
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

/**
 * Escapes HTML special characters to prevent XSS attacks.
 * Always use this when inserting user-provided text into innerHTML.
 *
 * Example: escapeHtml('<script>') → '&lt;script&gt;'
 */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

/**
 * Formats a date string into a readable format like "9 Apr 2026".
 * Returns '—' if the date is missing.
 */
function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/**
 * Redirects to login page if the user is not authenticated.
 * Call this at the top of protected pages (dashboard, tasks, habits).
 * Uses a quick /dashboard-stats ping to check session validity.
 */
async function requireLogin() {
  const { status } = await api.get("/dashboard-stats");
  if (status === 401) {
    window.location.href = "../pages/login.html";
  }
}
