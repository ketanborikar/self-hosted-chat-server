import sqlite3

# ✅ Consistent database path
DB_PATH = "/home/ubuntu/Project/app/database.db"

def init_db():
    """Initialize the database and ensure tables exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            recipient TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def validate_user(username):
    """Check if the user exists in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None  # ✅ Returns True if the user exists

def store_message(sender, recipient, message):
    """Store messages in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, recipient, message) VALUES (?, ?, ?)",
                   (sender, recipient, message))
    conn.commit()
    conn.close()

def get_offline_messages(recipient):
    """Retrieve offline messages when a user reconnects."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message FROM messages
        WHERE recipient = ? ORDER BY timestamp ASC
    """, (recipient,))

    messages = [f"{sender}: {message}" for sender, message in cursor.fetchall()]
    conn.close()
    return messages

def cleanup_old_messages():
    """Archive and delete messages older than 30 days."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ✅ Archive before deletion
    cursor.execute("""
        INSERT INTO archived_messages (sender, recipient, message, timestamp)
        SELECT sender, recipient, message, timestamp FROM messages
        WHERE timestamp < datetime('now', '-30 days')
    """)

    cursor.execute("DELETE FROM messages WHERE timestamp < datetime('now', '-30 days')")
    conn.commit()
    conn.close()

def get_offline_messages(recipient):
    conn = sqlite3.connect("/home/ubuntu/Project/app/database.db")
    cursor = conn.cursor()
    
    # ✅ Ensure only `sender, message` are returned (remove `timestamp`)
    cursor.execute("""
        SELECT sender, message FROM messages
        WHERE recipient = ? ORDER BY timestamp ASC
    """, (recipient,))

    messages = [(sender, message) for sender, message in cursor.fetchall()]  # ✅ Fix unpacking issue

    conn.close()
    return messages

# ✅ Initialize database when script runs
if __name__ == "__main__":
    init_db()
