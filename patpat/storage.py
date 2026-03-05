import json
import os
import uuid
from datetime import datetime
from pathlib import Path


class StorageManager:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(Path.home(), ".patpat", "history")
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _session_path(self, session_id: str) -> str | None:
        for f in os.listdir(self.base_dir):
            if f.endswith(f"_{session_id}.json"):
                return os.path.join(self.base_dir, f)
        return None

    def new_session_id(self) -> str:
        return uuid.uuid4().hex[:8]

    def save(self, messages: list[dict], session_id: str, emotion_tags: list[dict] = None):
        existing_path = self._session_path(session_id)
        now = datetime.now().isoformat()
        if existing_path:
            with open(existing_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            data["updated_at"] = now
            data["messages"] = messages
            if emotion_tags is not None:
                data["emotion_tags"] = emotion_tags
            path = existing_path
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{session_id}.json"
            path = os.path.join(self.base_dir, filename)
            data = {
                "session_id": session_id,
                "created_at": now,
                "updated_at": now,
                "messages": messages,
                "emotion_tags": emotion_tags or [],
            }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, session_id: str) -> dict | None:
        path = self._session_path(session_id)
        if path is None:
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_sessions(self) -> list[dict]:
        sessions = []
        for f in sorted(os.listdir(self.base_dir), reverse=True):
            if not f.endswith(".json"):
                continue
            path = os.path.join(self.base_dir, f)
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                user_msgs = [m for m in data.get("messages", []) if m.get("role") == "user"]
                preview = user_msgs[0]["content"][:40] if user_msgs else "(空会话)"
                sessions.append({
                    "session_id": data["session_id"],
                    "created_at": data.get("created_at", ""),
                    "message_count": len(data.get("messages", [])),
                    "preview": preview,
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return sessions
