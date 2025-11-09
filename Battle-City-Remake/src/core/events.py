from typing import Dict, List, Callable


class EventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, listener: Callable) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def unsubscribe(self, event_type: str, listener: Callable) -> None:
        if event_type in self._listeners and listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    def emit(self, event_type: str, *args, **kwargs) -> None:
        for listener in self._listeners.get(event_type, []):
            listener(*args, **kwargs)

    def clear(self) -> None:
        self._listeners.clear()
