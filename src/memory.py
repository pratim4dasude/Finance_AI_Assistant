from collections import defaultdict
from typing import Dict, List


class InMemorySessionStore:
    def __init__(self):
        self.sessions: Dict[str, List[dict]] = defaultdict(list)

    def add_turn(self, session_id: str, role: str, content: str):
        self.sessions[session_id].append({"role": role, "content": content})

    def get_history(self, session_id: str, limit: int = 6):
        return self.sessions[session_id][-limit:]


memory_store = InMemorySessionStore()