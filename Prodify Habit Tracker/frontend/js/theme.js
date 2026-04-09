/* ============================================================
   theme.js — Light / Dark Mode Toggle
   ============================================================
   Reads the saved theme from localStorage on page load,
   applies it to the <html> element, and wires up all toggle buttons.
   ============================================================ */

const THEME_KEY = 'prodify-theme'; // localStorage key for saving the preference

/**
 * Applies a theme by setting the data-theme attribute on <html>.
 * CSS uses this attribute to switch between light and dark color variables.
 * Also updates the theme icon on all toggle buttons.
 *
 * @param {string} theme - 'light' or 'dark'
 */
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);

  // Update all theme icons on the page (sun = light, moon = dark)
  document.querySelectorAll('.theme-icon-sun').forEach(el => {
    el.textContent = theme === 'dark' ? '🌙' : '☀️';
  });
}

/** Switches between light and dark mode. */
function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  applyTheme(current === 'light' ? 'dark' : 'light');
}

/**
 * Called on page load.
 * Restores the saved theme and attaches click listeners to all toggle buttons.
 */
function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || 'light';
  applyTheme(saved);

  // Attach the toggle to every element with class 'theme-toggle'
  document.querySelectorAll('.theme-toggle').forEach(btn => {
    btn.addEventListener('click', toggleTheme);
  });
}

// Run as soon as the page DOM is ready
document.addEventListener('DOMContentLoaded', initTheme);
