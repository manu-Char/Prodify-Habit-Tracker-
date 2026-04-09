/* ============================================================
   dashboard.js — Dashboard Stats & Previews
   ============================================================
   Loads and displays all dashboard data:
     - 5 stat counters (with count-up animation)
     - Latest 5 tasks preview panel
     - Habits overview panel
   Requires: api.js (for fetchDashboardStats + shared helpers)
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {
  loadDashboard();
});


/* ── Load all dashboard data ── */

async function loadDashboard() {
  const { ok, data } = await fetchDashboardStats();

  // BUG FIX: If not logged in (401), redirect to login page
  if (!ok) {
    if (data.status === 'error') {
      window.location.href = '../pages/login.html';
    }
    return;
  }

  const stats = data.stats || {};

  // Animate each stat counter from 0 up to its value
  animateCounter('stat-total-tasks',     stats.total_tasks     ?? 0);
  animateCounter('stat-completed-tasks', stats.completed_tasks ?? 0);
  animateCounter('stat-pending-tasks',   stats.pending_tasks   ?? 0);
  animateCounter('stat-total-habits',    stats.total_habits    ?? 0);
  animateCounter('stat-habits-today',    stats.habits_today    ?? 0);

  renderLatestTasks(data.latest_tasks    || []);
  renderHabitsOverview(data.habits_overview || []);
}


/* ── Animated counter ── */

/**
 * Animates a number element counting up from 0 to the target value.
 * BUG FIX: The original code used Math.ceil(value / 20) as the step,
 * which evaluates to 0 when value = 0, causing an infinite setInterval loop.
 * Fix: if value is 0, just set the text directly without animating.
 *
 * @param {string} elementId - ID of the element to update
 * @param {number} value     - Target number to count up to
 */
function animateCounter(elementId, value) {
  const el = document.getElementById(elementId);
  if (!el) return;

  // If value is 0, nothing to animate — just display it immediately
  if (value === 0) {
    el.textContent = 0;
    return;
  }

  let current = 0;
  const step  = Math.ceil(value / 20); // Reach target in ~20 steps

  const timer = setInterval(() => {
    current = Math.min(current + step, value);
    el.textContent = current;
    if (current >= value) clearInterval(timer);
  }, 40); // Update every 40ms (~25fps)
}


/* ── Latest tasks panel ── */

function renderLatestTasks(tasks) {
  const el = document.getElementById('latest-tasks');
  if (!el) return;

  if (tasks.length === 0) {
    el.innerHTML = `
      <div class="panel-empty">
        <div class="panel-empty-icon">📝</div>
        <p>No tasks yet. Go to Tasks to create one.</p>
      </div>`;
    return;
  }

  el.innerHTML = tasks.map(task => {
    const isCompleted = task.status === 'completed';
    return `
      <div class="task-card ${isCompleted ? 'completed' : ''}">
        <div class="task-checkbox ${isCompleted ? 'checked' : ''}">${isCompleted ? '✓' : ''}</div>
        <div class="task-body">
          <div class="task-title">${escapeHtml(task.title)}</div>
          ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ''}
          <div class="task-meta">
            <span class="badge ${isCompleted ? 'badge-completed' : 'badge-pending'}">
              ${isCompleted ? '✓ Completed' : '◷ Pending'}
            </span>
          </div>
        </div>
      </div>`;
  }).join('');
}


/* ── Habits overview panel ── */

function renderHabitsOverview(habits) {
  const el = document.getElementById('habits-overview');
  if (!el) return;

  const EMOJIS = ['🧘', '📚', '💧', '🏃', '🌿', '✍️', '🎯', '💪', '🌅', '🎵'];

  if (habits.length === 0) {
    el.innerHTML = `
      <div class="panel-empty">
        <div class="panel-empty-icon">🌱</div>
        <p>No habits yet. Go to Habits to create one.</p>
      </div>`;
    return;
  }

  el.innerHTML = habits.map((habit, i) => `
    <div class="habit-card ${habit.completed_today ? 'done-today' : ''}">
      <div class="habit-emoji">${EMOJIS[i % EMOJIS.length]}</div>
      <div class="habit-body">
        <div class="habit-name">${escapeHtml(habit.habit_name)}</div>
      </div>
      <div class="habit-actions">
        ${habit.completed_today
          ? `<div class="done-chip">✓ Done</div>`
          : `<span class="badge badge-pending">Pending</span>`
        }
      </div>
    </div>`).join('');
}
