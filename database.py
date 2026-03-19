"""
Database — JSON-based simple database for Miss Shasikala Bot
"""

import json
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "database", "db.json")
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)


class Database:
    def __init__(self):
        self._data = self._load()

    def _load(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"users": {}, "groups": {}, "premium": [], "banned": []}

    def save(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    # ── Users ─────────────────────────────
    def get_user(self, uid: int) -> dict:
        key = str(uid)
        if key not in self._data["users"]:
            self._data["users"][key] = {"limit": 20, "premium": False, "banned": False}
        return self._data["users"][key]

    def is_premium(self, uid: int) -> bool:
        return str(uid) in [str(i) for i in self._data.get("premium", [])]

    def add_premium(self, uid: int):
        if uid not in self._data["premium"]:
            self._data["premium"].append(uid)
        self.save()

    def remove_premium(self, uid: int):
        self._data["premium"] = [x for x in self._data["premium"] if x != uid]
        self.save()

    def is_banned(self, uid: int) -> bool:
        return uid in self._data.get("banned", [])

    def ban_user(self, uid: int):
        if uid not in self._data["banned"]:
            self._data["banned"].append(uid)
        self.save()

    def unban_user(self, uid: int):
        self._data["banned"] = [x for x in self._data["banned"] if x != uid]
        self.save()

    # ── Groups ────────────────────────────
    def get_group(self, cid: int) -> dict:
        key = str(cid)
        if key not in self._data["groups"]:
            self._data["groups"][key] = {
                "welcome": False,
                "goodbye": False,
                "antilink": False,
                "antispam": False,
                "welcome_text": "",
                "goodbye_text": "",
            }
        return self._data["groups"][key]

    def set_group(self, cid: int, key: str, value):
        g = self.get_group(cid)
        g[key] = value
        self.save()


db = Database()
