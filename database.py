import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_message TEXT,
            ai_reply TEXT,
            char_count INTEGER,
            passed_validation INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_message(session_id, user_message, ai_reply, passed_validation):
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO conversations 
        (session_id, user_message, ai_reply, char_count, passed_validation, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        session_id,
        user_message,
        ai_reply,
        len(ai_reply),
        1 if passed_validation else 0,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def get_all_conversations():
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('SELECT * FROM conversations ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = sqlite3.connect('conversations.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM conversations')
    total = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM conversations WHERE passed_validation = 1')
    passed = c.fetchone()[0]
    c.execute('SELECT AVG(char_count) FROM conversations')
    avg_chars = c.fetchone()[0]
    c.execute('SELECT user_message FROM conversations ORDER BY timestamp DESC LIMIT 5')
    recent = [r[0] for r in c.fetchall()]
    conn.close()
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "avg_chars": round(avg_chars or 0),
        "recent_topics": recent
    }

if __name__ == '__main__':
    init_db()
    print("Database created successfully!")
    print("Tables: conversations")
