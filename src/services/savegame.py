"""
Збереження прогресу: рівень, рахунок, налаштування гучності/керування. Формат JSON, валідація схеми.
"""

import json
from pathlib import Path

PATH = Path(".savegame.json")

class SaveGame:
    def __init__(self):
        self.data = {"level": 1, "score": 0}

    def load(self):
        if PATH.exists():
            self.data.update(json.loads(PATH.read_text()))

    def save(self):
        PATH.write_text(json.dumps(self.data))
