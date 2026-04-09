import mysql.connector
from mysql.connector import Error

# ── Database configuration ────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "prodify_db",
    "port": 3306,
    "autocommit": True
}


# ── Create database if not exists ─────────────────────────────
def create_database_if_not_exists():
    try:
        temp_conn = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            port=DB_CONFIG["port"]
        )
        cursor = temp_conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.close()
        temp_conn.close()
    except Error as e:
        print(f"[DB ERROR] Database creation failed: {e}")


# ── Get connection ────────────────────────────────────────────
def get_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"[DB ERROR] Connection failed: {e}")
    return None


# ── Initialize tables ─────────────────────────────────────────
def init_db():
    create_database_if_not_exists()

    conn = get_connection()
    if not conn:
        print("[DB ERROR] Cannot initialise — no connection.")
        return

    cursor = conn.cursor()

    try:
        # USERS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                email VARCHAR(200) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # TASKS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                status ENUM('pending','completed') DEFAULT 'pending',
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_date DATETIME DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # HABITS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                habit_name VARCHAR(200) NOT NULL,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # HABIT LOGS
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                habit_id INT NOT NULL,
                completion_date DATE NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                UNIQUE KEY unique_habit_day (habit_id, completion_date)
            )
        """)

        print("[DB] Tables initialized successfully.")

    except Error as e:
        print(f"[DB ERROR] Table creation failed: {e}")

    finally:
        cursor.close()
        conn.close()