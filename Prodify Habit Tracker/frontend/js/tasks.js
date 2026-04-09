/* ============================================================
   tasks.js — Task Manager Logic
   ============================================================
   Handles loading, displaying, creating, completing, and deleting tasks.
   Requires: api.js (for API functions + shared helpers like showToast)
   ============================================================ */

// All tasks loaded from the server — stored here for client-side filtering
let allTasks = [];

document.addEventListener('DOMContentLoaded', () => {
  loadTasks();
  bindTaskForm();
});


/* ── Load tasks from server ── */

async function loadTasks() {
  showTasksLoading(true);
  const { ok, data } = await fetchTasks();
  showTasksLoading(false);

  if (!ok) {
    showToast('Failed to load tasks', 'error');
    return;
  }

  allTasks = data.tasks || [];
  renderTasks(allTasks);
}


/* ── Render tasks to the DOM ── */

function renderTasks(tasks) {
  const list = document.getElementById('task-list');
  if (!list) return;

  if (tasks.length === 0) {
    list.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📝</div>
        <h3>No tasks yet</h3>
        <p>Add your first task using the form above.</p>
      </div>`;
    return;
  }

  list.innerHTML = tasks.map((task, index) => buildTaskCardHTML(task, index)).join('');
  attachTaskEventListeners(list);
}

/**
 * Builds the HTML string for a single task card.
 * @param {object} task  - Task object from the API
 * @param {number} index - Used to stagger the animation delay
 */
function buildTaskCardHTML(task, index) {
  const isCompleted = task.status === 'completed';
  const delay       = Math.min(index * 0.06, 0.5); // Stagger animation, max 0.5s

  return `
    <div class="task-card ${isCompleted ? 'completed' : ''}" data-id="${task.id}" style="animation-delay:${delay}s">
      <div class="task-checkbox ${isCompleted ? 'checked' : ''}" data-action="complete" title="${isCompleted ? 'Completed' : 'Mark complete'}">
        ${isCompleted ? '✓' : ''}
      </div>
      <div class="task-body">
        <div class="task-title">${escapeHtml(task.title)}</div>
        ${task.description ? `<div class="task-desc">${escapeHtml(task.description)}</div>` : ''}
        <div class="task-meta">
          <span class="badge ${isCompleted ? 'badge-completed' : 'badge-pending'}">
            ${isCompleted ? '✓ Completed' : '◷ Pending'}
          </span>
          <span class="task-date">📅 ${formatDate(task.created_date)}</span>
        </div>
      </div>
      <div class="task-actions">
        ${!isCompleted ? `<button class="btn btn-success-soft btn-sm" data-action="complete" title="Mark complete">✓</button>` : ''}
        <button class="btn btn-danger-soft btn-sm" data-action="delete" title="Delete task">🗑</button>
      </div>
    </div>`;
}

/**
 * Attaches click listeners to all action buttons inside the task list.
 * Uses event delegation via data-action attributes.
 */
function attachTaskEventListeners(container) {
  container.querySelectorAll('[data-action]').forEach(el => {
    el.addEventListener('click', async (e) => {
      const card   = e.target.closest('[data-id]');
      const id     = card?.dataset.id;
      const action = el.dataset.action;
      if (!id) return;

      if (action === 'complete') await handleCompleteTask(id, card);
      if (action === 'delete')   await handleDeleteTask(id, card);
    });
  });
}


/* ── Task action handlers ── */

async function handleCompleteTask(id) {
  const { ok, data } = await completeTask(id);
  if (!ok) {
    showToast(data.message || 'Error', 'error');
    return;
  }
  showToast('Task marked as complete! ✓', 'success');
  loadTasks(); // Refresh list from server
}

async function handleDeleteTask(id, card) {
  card.style.opacity = '0.4'; // Visual feedback while waiting

  const { ok, data } = await deleteTask(id);
  if (!ok) {
    card.style.opacity = '1';
    showToast(data.message || 'Error', 'error');
    return;
  }

  showToast('Task deleted.', 'info');

  // Animate the card out before refreshing
  card.style.transition = 'all 0.3s ease';
  card.style.transform  = 'translateX(20px)';
  card.style.opacity    = '0';
  setTimeout(() => loadTasks(), 300);
}


/* ── Add task form ── */

function bindTaskForm() {
  const form = document.getElementById('task-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = form.querySelector('#task-title').value.trim();
    const desc  = form.querySelector('#task-desc').value.trim();

    if (!title) {
      showToast('Please enter a task title.', 'error');
      return;
    }

    const btn = form.querySelector('[type="submit"]');
    btn.disabled    = true;
    btn.textContent = 'Adding...';

    const { ok, data } = await createTask(title, desc);

    btn.disabled    = false;
    btn.textContent = '+ Add Task';

    if (!ok) {
      showToast(data.message || 'Failed to add task.', 'error');
      return;
    }

    showToast('Task added successfully!', 'success');
    form.reset();
    loadTasks();
  });
}


/* ── Filter tasks (client-side, no server call needed) ── */

/**
 * Filters the currently displayed tasks by status without reloading from server.
 * Called by the filter buttons in tasks.html.
 *
 * @param {string} filter - 'all', 'pending', or 'completed'
 */
function filterTasks(filter) {
  if (filter === 'all') {
    renderTasks(allTasks);
  } else {
    renderTasks(allTasks.filter(t => t.status === filter));
  }
}


/* ── Loading state toggle ── */

function showTasksLoading(show) {
  const loadingEl = document.getElementById('tasks-loading');
  const listEl    = document.getElementById('task-list');
  if (loadingEl) loadingEl.classList.toggle('hidden', !show);
  if (listEl)    listEl.classList.toggle('hidden', show);
}
