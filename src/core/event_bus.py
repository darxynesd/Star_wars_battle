"""
типи подій гри (вистріл, підбір бонусу, смерть, перехід сцени), правила підписки/розсилки між системами та сутностями.
"""
from collections import defaultdict
from typing import Callable, Dict, List, Any

class EventBus:
    def __init__(self):
        self._subs: Dict[str, List[Callable]] = defaultdict(list)

    def on(self, event: str, handler: Callable[[Any], None]):
        self._subs[event].append(handler)

    def emit(self, event: str, payload: Any = None):
        for h in list(self._subs.get(event, [])):
            h(payload)

# назви подій
EV_SHOOT = "shoot"
EV_HIT = "hit"
EV_POWERUP = "powerup"
EV_GAME_OVER = "game_over"
EV_NEXT_LEVEL = "next_level"
EV_PAUSE = "pause"
