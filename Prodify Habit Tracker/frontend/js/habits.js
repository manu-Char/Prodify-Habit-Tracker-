/* ============================================================
   habits.js — Habit Tracker Logic
   ============================================================
   Handles loading, displaying, creating, completing, and deleting habits.
   Requires: api.js (for API functions + shared helpers like showToast)
   ============================================================ */

// Emoji pool — each habit gets an emoji based on its position in the list
const HABIT_EMOJIS = ['🧘', '📚', '💧', '🏃', '🌿', '✍️', '🎯', '💪', '🌅', '🎵'];

document.addEventListener('DOMContentLoaded', () => {
  loadHabits();
  bindHabitForm();
});


/* ── Load habits from server ── */

async function loadHabits() {
  showHabitsLoading(true);
  const { ok, data } = await fetchHabits();
  showHabitsLoading(false);

  if (!ok) {
    showToast('Failed to load habits.', 'error');
    return;
  }

  renderHabits(data.habits || []);
}


/* ── Render habits to the DOM ── */

function renderHabits(habits) {
  const list = document.getElementById('habit-list');
  if (!list) return;

  if (habits.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">🌱</div>
        <h3>No habits yet</h3>
        <p>Add a habit above to start tracking your daily progress.</p>
      </div>`;
    return;
  }

  list.innerHTML = habits.map((habit, index) => buildHabitCardHTML(habit, index)).join('');
  attachHabitEventListeners(list);
}

/**
 * Builds the HTML for a single habit card.
 * @param {object} habit - Habit object from the API (includes completed_today)
 * @param {number} index - Used for emoji and animation delay
 */
function buildHabitCardHTML(habit, index) {
  const isDoneToday = habit.completed_today;
  const emoji       = HABIT_EMOJIS[index % HABIT_EMOJIS.length];
  const delay       = Math.min(index * 0.06, 0.5);

  return `
    <div class="habit-card ${isDoneToday ? 'done-today' : ''}" data-id="${habit.id}" style="animation-delay:${delay}s">
      <div class="habit-emoji">${emoji}</div>
      <div class="habit-body">
        <div class="habit-name">${escapeHtml(habit.habit_name)}</div>
        <div class="habit-since">Started ${formatDate(habit.created_date)}</div>
      </div>
      <div class="habit-actions">
        ${isDoneToday
          ? `<div class="done-chip"><span>✓</span> Done Today</div>`
          : `<button class="btn btn-teal-soft btn-sm" data-action="complete">Mark Done</button>`
        }
        <button class="btn btn-danger-soft btn-sm btn-icon" data-action="delete" title="Remove habit">🗑</button>
      </div>
    </div>`;
}

/**
 * Attaches click listeners to all action buttons in the habit list.
 */
function attachHabitEventListeners(container) {
  container.querySelectorAll('[data-action]').forEach(el => {
    el.addEventListener('click', async (e) => {
      const card   = e.target.closest('[data-id]');
      const id     = card?.dataset.id;
      const action = el.dataset.action;
      if (!id) return;

      if (action === 'complete') await handleCompleteHabit(id, el);
      if (action === 'delete')   await handleDeleteHabit(id, card);
    });
  });
}


/* ── Habit action handlers ── */

async function handleCompleteHabit(id, btn) {
  btn.disabled    = true;
  btn.textContent = '...';

  const { ok, data } = await completeHabit(id);
  if (!ok) {
    showToast(data.message || 'Error', 'error');
    btn.disabled    = false;
    btn.textContent = 'Mark Done';
    return;
  }

  showToast('Habit completed for today! 🎉', 'success');
  loadHabits(); // Refresh to show "Done Today" chip
}

async function handleDeleteHabit(id, card) {
  if (!confirm('Remove this habit and all its history?')) return;

  // BUG FIX: was calling api.delete() directly (undefined), now calls deleteHabit() from api.js
  const { ok, data } = await deleteHabit(id);
  if (!ok) {
    showToast(data.message || 'Error', 'error');
    return;
  }

  showToast('Habit removed.', 'info');

  // Animate card out before refreshing
  card.style.transition = 'all 0.3s ease';
  card.style.transform  = 'translateX(20px)';
  card.style.opacity    = '0';
  setTimeout(() => loadHabits(), 300);
}


/* ── Add habit form ── */

function bindHabitForm() {
  const form = document.getElementById('habit-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const name = form.querySelector('#habit-name').value.trim();
    if (!name) {
      showToast('Please enter a habit name.', 'error');
      return;
    }

    const btn = form.querySelector('[type="submit"]');
    btn.disabled    = true;
    btn.textContent = 'Adding...';

    const { ok, data } = await createHabit(name);

    btn.disabled    = false;
    btn.textContent = '+ Add Habit';

    if (!ok) {
      showToast(data.message || 'Failed to add habit.', 'error');
      return;
    }

    showToast('Habit added!', 'success');
    form.reset();
    loadHabits();
  });
}


/* ── Loading state toggle ── */

function showHabitsLoading(show) {
  const loadingEl = document.getElementById('habits-loading');
  const listEl    = document.getElementById('habit-list');
  if (loadingEl) loadingEl.classList.toggle('hidden', !show);
  if (listEl)    listEl.classList.toggle('hidden', show);
}
