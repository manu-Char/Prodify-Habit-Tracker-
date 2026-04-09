# Prodify — Backend Setup Guide

## Project Folder Structure

```
prodify/
│
├── frontend/                 ← Frontend (HTML, CSS, JS)
│   ├── index.html
│   ├── css/style.css
│   ├── js/
│   │   ├── api.js            ← API calls + shared helpers (escapeHtml, showToast, formatDate)
│   │   ├── theme.js          ← Light/dark mode toggle
│   │   ├── tasks.js          ← Task page logic
│   │   ├── habits.js         ← Habits page logic
│   │   └── dashboard.js      ← Dashboard stats logic
│   └── pages/
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── tasks.html
│       └── habits.html
│
└── backend/                  ← Backend (Python Flask)
    ├── app.py                ← Main entry point
    ├── db.py                 ← Database connection + table creation
    ├── routes/
    │   ├── auth.py           ← Register / Login / Logout
    │   ├── tasks.py          ← Task CRUD routes
    │   ├── habits.py         ← Habit routes
    │   └── dashboard.py      ← Dashboard stats route
    ├── database/
    │   └── schema.sql        ← Database setup SQL (optional — db.py auto-creates tables)
    ├── requirements.txt      ← Python dependencies
    └── README.md             ← This file
```

---

## Local Setup with XAMPP

### Step 1 — Install Python packages

```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Start XAMPP

- Open XAMPP Control Panel
- Start **Apache** and **MySQL**

### Step 3 — Create the Database

- Open browser → `http://localhost/phpmyadmin`
- Click **New** → name it `prodify_db` → click **Create**

> **Note:** You can skip manually running schema.sql — `init_db()` in `db.py` will
> auto-create all tables when `app.py` starts.

### Step 4 — Run the backend

```bash
cd backend
python app.py
```

### Step 5 — Open the app

```
http://localhost:5000
```

---

## API Endpoints Reference

| Method | Endpoint              | Description                          | Auth Required |
|--------|-----------------------|--------------------------------------|---------------|
| POST   | /register             | Create new user account              | No            |
| POST   | /login                | Login and start session              | No            |
| GET    | /logout               | Logout and clear session             | No            |
| GET    | /tasks                | Get all tasks for user               | Yes           |
| POST   | /tasks                | Create a new task                    | Yes           |
| PUT    | /tasks/\<id\>         | Mark task as completed               | Yes           |
| DELETE | /tasks/\<id\>         | Delete a task                        | Yes           |
| GET    | /habits               | Get all habits + today's status      | Yes           |
| POST   | /habits               | Create a new habit                   | Yes           |
| POST   | /habits/complete      | Mark habit done today                | Yes           |
| DELETE | /habits/\<id\>        | Delete a habit                       | Yes           |
| GET    | /dashboard-stats      | Get all dashboard data               | Yes           |

---

## Bug Fixes (v2)

The following bugs were found and fixed in this version:

### 1. Username not saved after login
**File:** `js/api.js` — `authLogin()`
**Problem:** After a successful login, the username was not saved to `localStorage`,
so the dashboard avatar always showed "U" and the welcome message never appeared.
**Fix:** `authLogin()` now saves the username to `localStorage` on success.

### 2. Delete habit crash
**File:** `js/habits.js` — `handleDeleteHabit()`
**Problem:** The function called `api.delete(...)` directly, but `api` is only
defined inside `api.js` and `delete` is a reserved JS keyword — the call was broken.
**Fix:** Changed to call `deleteHabit(id)`, the named function defined in `api.js`.

### 3. Dashboard counter infinite loop when value is 0
**File:** `js/dashboard.js` — `animateCounter()`
**Problem:** The step was calculated as `Math.ceil(value / 20)`. When `value = 0`,
this gives `step = 0`, so `current` never reaches `value` and `setInterval` runs forever.
**Fix:** Added an early return: if `value === 0`, just set the text directly and skip the animation.

### 4. Dashboard doesn't redirect unauthenticated users
**File:** `js/dashboard.js` — `loadDashboard()`
**Problem:** If a user opened the dashboard URL directly without being logged in,
the API returned a 401 error but the page just showed empty panels silently.
**Fix:** On a failed API response, the page now redirects to `login.html`.

### 5. Filter buttons broken after task actions
**File:** `frontend/pages/tasks.html`
**Problem:** The filter buttons used inline DOM manipulation (hiding/showing existing cards).
After completing or deleting a task, the list was reloaded but the active filter was lost,
and cards reappeared without proper event listeners.
**Fix:** Filter buttons now call `filterTasks(filter)` from `tasks.js`, which re-renders
from the in-memory `allTasks` array so event listeners are always fresh.

### 6. Duplicate helper functions
**Files:** `js/tasks.js`, `js/habits.js`
**Problem:** `showToast()`, `escapeHtml()`, and `formatDate()` were copy-pasted into
both files — a maintenance problem (bug fix in one place, not the other).
**Fix:** Moved all three to `api.js` (loaded by every page), removed the duplicates.

### 7. DB: missing UNIQUE constraint on habit_logs
**File:** `backend/db.py` — `init_db()`
**Problem:** The `habit_logs` table had no database-level constraint to prevent
duplicate completions on the same day — only application code enforced the rule.
**Fix:** Added `UNIQUE KEY unique_habit_day (habit_id, completion_date)` to the table.

---

## PythonAnywhere Deployment

### Step 1 — Upload files

- Log into PythonAnywhere
- Open a **Bash console**
- Upload the `frontend/` and `backend/` folders

### Step 2 — Install packages

```bash
pip3 install --user flask flask-cors mysql-connector-python werkzeug
```

### Step 3 — Create MySQL database

- Go to **Databases** tab on PythonAnywhere
- Create a new database (e.g. `yourusername$prodify_db`)
- Note the host, username, and password

### Step 4 — Update db.py

Open `backend/db.py` and update `DB_CONFIG`:

```python
DB_CONFIG = {
    "host":     "yourusername.mysql.pythonanywhere-services.com",
    "user":     "yourusername",
    "password": "your_database_password",
    "database": "yourusername$prodify_db",
    "port":     3306,
}
```

### Step 5 — Create Web App

- Go to **Web** tab → **Add a new web app**
- Choose **Flask** → Python 3.10
- Set Source code path to your `backend/` folder
- Set WSGI file — replace contents with:

```python
import sys
sys.path.insert(0, '/home/yourusername/backend')
from app import app as application
```

### Step 6 — Reload & Test

- Click **Reload** on the Web tab
- Visit `https://yourusername.pythonanywhere.com`

---

## JSON Response Format

All API responses follow this format:

**Success:**
```json
{ "status": "success", "message": "Done" }
```

**Error:**
```json
{ "status": "error", "message": "Task not found" }
```

---

## Default XAMPP Credentials

| Field    | Value        |
|----------|--------------|
| Host     | localhost    |
| User     | root         |
| Password | *(empty)*    |
| Database | prodify_db   |
| Port     | 3306         |
