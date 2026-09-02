import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "learning.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_name  TEXT NOT NULL,
                content     TEXT NOT NULL,
                source_url  TEXT,
                saved_at    DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id    INTEGER REFERENCES topics(id) ON DELETE CASCADE,
                role        TEXT NOT NULL,
                message     TEXT NOT NULL,
                sent_at     DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_topic(topic_name, content, source_url):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO topics (topic_name, content, source_url) VALUES (?, ?, ?)",
            (topic_name, content, source_url)
        )
        conn.commit()
        return cursor.lastrowid


def get_all_topics():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, topic_name, source_url, saved_at FROM topics ORDER BY saved_at DESC"
        ).fetchall()
    return rows


def get_topic_by_id(topic_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, topic_name, content, source_url, saved_at FROM topics WHERE id = ?",
            (topic_id,)
        ).fetchone()
    return row


def delete_topic(topic_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        conn.commit()


def save_chat_message(topic_id, role, message):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (topic_id, role, message) VALUES (?, ?, ?)",
            (topic_id, role, message)
        )
        conn.commit()


def get_chat_history(topic_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, message FROM chat_history WHERE topic_id = ? ORDER BY sent_at ASC",
            (topic_id,)
        ).fetchall()
    return rows


def search_topics(keyword):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, topic_name, source_url, saved_at FROM topics WHERE topic_name LIKE ? ORDER BY saved_at DESC",
            (f"%{keyword}%",)
        ).fetchall()
    return rows
