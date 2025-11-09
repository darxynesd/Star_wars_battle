import json
import os


SAVE_FILE = os.path.join(os.path.dirname(__file__), "savegame.json")


def _default():
    return {"level": 1, "score": 0, "settings": {"volume": 100, "controls": {}}}


def load_game():
    if not os.path.exists(SAVE_FILE):
        return _default()
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "level" not in data or "score" not in data:
            return _default()
        return data
    except Exception:
        return _default()


def save_game(data: dict):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
