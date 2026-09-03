import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path("data/conversations.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            turn_number INTEGER NOT NULL,
            agent_name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
        )
        """
    )

    conn.commit()
    conn.close()


def create_conversation(user_question):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (
            user_question,
            created_at
        )
        VALUES (?, ?)
        """,
        (
            user_question,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    conversation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return conversation_id


def save_message(
    conversation_id,
    turn_number,
    agent_name,
    message,
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages (
            conversation_id,
            turn_number,
            agent_name,
            message,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            conversation_id,
            turn_number,
            agent_name,
            message,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()

    print(f"DB 생성 완료: {DB_PATH}")