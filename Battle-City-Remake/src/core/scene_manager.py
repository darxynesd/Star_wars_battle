import pygame
from typing import Dict, Optional


class IScene:
    def enter(self): ...
    def exit(self): ...
    def handle_event(self, event: pygame.event.Event): ...
    def update(self, dt: float): ...
    def draw(self, screen: pygame.Surface): ...


# game/core/scene_manager.py (додай методи push/pop, і не чіпай change() для інших переходів)
class SceneManager:
    def __init__(self):
        self._scenes = {}
        self.current = None
        self.current_name = None
        self._stack = []  # ← стек активних сцен

    def register(self, name, scene):
        self._scenes[name] = scene

    def change(self, name):
        # звичайний “жорсткий” перехід (exit попередньої, enter нової)
        if self.current:
            self.current.exit()
        self.current = self._scenes[name]
        self.current_name = name
        self.current.enter()

    # нове: м'яке накладання сцени поверх (для паузи)
    def push(self, name):
        if self.current:
            self._stack.append(self.current)  # не викликаємо exit()
        self.current = self._scenes[name]
        self.current_name = name
        self.current.enter()

    def pop(self):
        if self.current:
            self.current.exit()
        self.current = self._stack.pop() if self._stack else None
        # current уже “в грі”, тому enter() не викликаємо повторно
