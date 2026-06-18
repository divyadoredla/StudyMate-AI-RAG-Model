import sqlite3
import bcrypt

DB_PATH = "app.db"

def init_db():
    """Initializes the database and creates the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    """Hashes the password and adds a new user to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def verify_user(username, password):
    """Verifies a user's password against the stored hash."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result is None:
        return False  # User not found

    stored_hash = result[0]
    password_bytes = password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, stored_hash)
