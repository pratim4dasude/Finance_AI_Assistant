# import re
# from collections import defaultdict
# from typing import Dict, List, Optional
#
#
# class InMemorySessionStore:
#     def __init__(self):
#         self.sessions: Dict[str, List[dict]] = defaultdict(list)
#         self.session_state: Dict[str, dict] = defaultdict(dict)
#
#     def add_turn(self, session_id: str, role: str, content: str):
#         self.sessions[session_id].append(
#             {
#                 "role": role,
#                 "content": content,
#             }
#         )
#
#         if role == "user":
#             ticker = self._extract_ticker(content)
#             if ticker:
#                 self.session_state[session_id]["last_ticker"] = ticker
#
#     def get_history(self, session_id: str, limit: int = 6):
#         return self.sessions[session_id][-limit:]
#
#     def get_state(self, session_id: str):
#         return self.session_state[session_id]
#
#     def resolve_follow_up(self, session_id: str, query: str) -> str:
#         """
#         Resolves simple follow-ups like:
#         - What about its risk?
#         - How is it doing?
#         - Should I buy more?
#         """
#         state = self.get_state(session_id)
#         last_ticker = state.get("last_ticker")
#
#         if not last_ticker:
#             return query
#
#         q = query.lower()
#
#         follow_up_words = ["it", "its", "that", "this", "stock", "company"]
#
#         if any(word in q.split() for word in follow_up_words):
#             return f"{query} Context: the user is referring to {last_ticker}."
#
#         return query
#
#     def _extract_ticker(self, text: str) -> Optional[str]:
#         ticker_map = {
#             "apple": "AAPL",
#             "aapl": "AAPL",
#             "nvidia": "NVDA",
#             "nvda": "NVDA",
#             "tesla": "TSLA",
#             "tsla": "TSLA",
#             "asml": "ASML",
#             "microsoft": "MSFT",
#             "msft": "MSFT",
#             "google": "GOOGL",
#             "alphabet": "GOOGL",
#             "amazon": "AMZN",
#         }
#
#         text_lower = text.lower()
#
#         for key, ticker in ticker_map.items():
#             if re.search(rf"\b{re.escape(key)}\b", text_lower):
#                 return ticker
#
#         return None
#
#
# memory_store = InMemorySessionStore()


import json
import os
import re
import sqlite3
from typing import List, Optional


class SQLiteSessionStore:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL", "sqlite:///./valura_memory.db")
        self.db_path = db_url.replace("sqlite:///", "")
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    last_ticker TEXT,
                    user_context_json TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            conn.commit()

    def add_turn(self, session_id: str, role: str, content: str):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (session_id, role, content)
                VALUES (?, ?, ?)
                """,
                (session_id, role, content),
            )
            conn.commit()

        if role == "user":
            ticker = self._extract_ticker(content)
            if ticker:
                self.update_state(session_id, {"last_ticker": ticker})

    def get_history(self, session_id: str, limit: int = 6) -> List[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, content
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

        rows.reverse()
        return [{"role": role, "content": content} for role, content in rows]

    def save_user_context(self, session_id: str, user_context: dict):
        current = self.get_state(session_id)
        last_ticker = current.get("last_ticker")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO session_state (session_id, last_ticker, user_context_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id)
                DO UPDATE SET
                    user_context_json = excluded.user_context_json,
                    last_ticker = COALESCE(session_state.last_ticker, excluded.last_ticker),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, last_ticker, json.dumps(user_context)),
            )
            conn.commit()

    def get_saved_user_context(self, session_id: str) -> Optional[dict]:
        state = self.get_state(session_id)
        raw = state.get("user_context_json")

        if not raw:
            return None

        try:
            return json.loads(raw)
        except Exception:
            return None

    def update_state(self, session_id: str, updates: dict):
        current = self.get_state(session_id)

        last_ticker = updates.get("last_ticker", current.get("last_ticker"))
        user_context_json = current.get("user_context_json")

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO session_state (session_id, last_ticker, user_context_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(session_id)
                DO UPDATE SET
                    last_ticker = excluded.last_ticker,
                    user_context_json = COALESCE(session_state.user_context_json, excluded.user_context_json),
                    updated_at = CURRENT_TIMESTAMP
                """,
                (session_id, last_ticker, user_context_json),
            )
            conn.commit()

    def get_state(self, session_id: str) -> dict:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT last_ticker, user_context_json
                FROM session_state
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()

        if not row:
            return {}

        return {
            "last_ticker": row[0],
            "user_context_json": row[1],
        }

    def resolve_follow_up(self, session_id: str, query: str) -> str:
        state = self.get_state(session_id)
        last_ticker = state.get("last_ticker")

        if not last_ticker:
            return query

        q = query.lower()
        follow_up_words = ["it", "its", "that", "this", "stock", "company"]

        if any(word in q.split() for word in follow_up_words):
            return f"{query} about {last_ticker}"

        return query

    def _extract_ticker(self, text: str) -> Optional[str]:
        ticker_map = {
            "apple": "AAPL",
            "aapl": "AAPL",
            "nvidia": "NVDA",
            "nvda": "NVDA",
            "tesla": "TSLA",
            "tsla": "TSLA",
            "asml": "ASML",
            "microsoft": "MSFT",
            "msft": "MSFT",
            "google": "GOOGL",
            "alphabet": "GOOGL",
            "amazon": "AMZN",
        }

        text_lower = text.lower()

        for key, ticker in ticker_map.items():
            if re.search(rf"\b{re.escape(key)}\b", text_lower):
                return ticker

        return None


memory_store = SQLiteSessionStore()