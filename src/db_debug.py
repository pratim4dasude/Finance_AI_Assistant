import sqlite3
import json
from typing import Optional

DB_PATH = "valura_memory.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def show_full_database():
    with get_connection() as conn:
        messages = conn.execute(
            """
            SELECT session_id, role, content
            FROM messages
            ORDER BY session_id, id
            """
        ).fetchall()

        states = conn.execute(
            """
            SELECT session_id, last_ticker, user_context_json
            FROM session_state
            """
        ).fetchall()

    print("\n--------------- DATABASE --------\n")

    print("MESSAGES:\n")

    if not messages:
        print("No messages found.\n")
    else:
        current_session = None
        for session_id, role, content in messages:
            if session_id != current_session:
                current_session = session_id
                print(f"\nSession: {session_id}")
                print("-" * 40)

            print(f"{role.upper()}: {content}")

    print("\n\nSESSION STATE:\n")

    if not states:
        print("No session state found.\n")
    else:
        for session_id, last_ticker, context_json in states:
            print(f"\nSession: {session_id}")
            print(f"Last ticker: {last_ticker}")

            if context_json:
                try:
                    parsed = json.loads(context_json)
                    print("User context:")
                    print(json.dumps(parsed, indent=2))
                except Exception:
                    print("User context (raw):", context_json)
            else:
                print("User context: None")

    print("\n----------------- END -------------\n")

def list_sessions():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT session_id FROM messages"
        ).fetchall()

    print("\nSessions:")
    for row in rows:
        print(f"- {row[0]}")

    print(f"\nTotal sessions: {len(rows)}")


def count_sessions():
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM messages"
        ).fetchone()

    print(f"Total sessions: {row[0]}")


def get_session_messages(session_id: str):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT role, content
            FROM messages
            WHERE session_id = ?
            ORDER BY id
            """,
            (session_id,),
        ).fetchall()

    print(f"\nMessages for session: {session_id}\n")

    if not rows:
        print("No messages found.")
        return

    for role, content in rows:
        print(f"{role.upper()}: {content}\n")


def get_user_context(session_id: str):
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT user_context_json
            FROM session_state
            WHERE session_id = ?
            """,
            (session_id,),
        ).fetchone()

    if not row:
        print("No user context found.")
        return

    try:
        context = json.loads(row[0])
    except Exception:
        print("Failed to parse user context.")
        return

    print(f"\nUser context for session: {session_id}\n")
    print(json.dumps(context, indent=2))


def delete_session(session_id: str):
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM messages WHERE session_id = ?",
            (session_id,),
        )
        conn.execute(
            "DELETE FROM session_state WHERE session_id = ?",
            (session_id,),
        )
        conn.commit()

    print(f"Session '{session_id}' deleted.")


def delete_all_data():
    with get_connection() as conn:
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM session_state")
        conn.commit()

    print("All session data deleted.")


if __name__ == "__main__":
    show_full_database()

    # list_sessions()

    # count_sessions()

    # get_session_messages("sqlite_memory_1")

    # get_user_context("sqlite_memory_1")

    # delete_session("sqlite_memory_1")

    # delete_all_data()