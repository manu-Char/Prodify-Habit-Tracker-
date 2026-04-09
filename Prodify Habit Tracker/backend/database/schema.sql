-- ============================================================
--  PRODIFY DATABASE SCHEMA
--  Run this in phpMyAdmin (XAMPP) or PythonAnywhere MySQL
-- ============================================================

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS prodify_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE prodify_db;

-- ── Users ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(100)  NOT NULL,
    email         VARCHAR(200)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    created_at    DATETIME      DEFAULT CURRENT_TIMESTAMP
);

-- ── Tasks ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS tasks (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT           NOT NULL,
    title          VARCHAR(200)  NOT NULL,
    description    TEXT,
    status         ENUM('pending', 'completed') DEFAULT 'pending',
    created_date   DATETIME      DEFAULT CURRENT_TIMESTAMP,
    completed_date DATETIME      DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Habits ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS habits (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT           NOT NULL,
    habit_name   VARCHAR(200)  NOT NULL,
    created_date DATETIME      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ── Habit Logs ───────────────────────────────────────────────
--  One row per habit per day when completed.
--  Enforces the "one completion per day" rule.
CREATE TABLE IF NOT EXISTS habit_logs (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    habit_id        INT  NOT NULL,
    completion_date DATE NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
);

-- ── Optional: Verify tables created ─────────────────────────
SHOW TABLES;
