import sqlite3
DB_PATH = "/home/ubuntu/Project/chat_history.db"  # ✅ Use absolute path

def validate_user(username):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user is not None  # ✅ Returns True if the user exists


def init_db():
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
    conn.commit()
    conn.close()

def store_message(sender, recipient, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, recipient, message) VALUES (?, ?, ?)", 
                   (sender, recipient, message))
    conn.commit()
    conn.close()

def get_offline_messages(recipient):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message, timestamp FROM messages 
        WHERE recipient = ? ORDER BY timestamp ASC
    """, (recipient,))
    
    messages = []
    seen_messages = set()
    for sender, message, timestamp in cursor.fetchall():
        msg_key = f"{sender}:{message}"
        if msg_key not in seen_messages:
            messages.append(f"{sender}: {message}")
            seen_messages.add(msg_key)
    
    conn.close()
    return messages

def cleanup_old_messages():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE timestamp < datetime('now', '-30 days')")
    conn.commit()
    conn.close()
