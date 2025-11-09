"""
Логіка головного меню: кнопки «Грати», «Налаштування» (мінімально — звук/керування), «Вийти». Переходи на game_scene. Завантаження фону/логотипу з assets.
"""

import pygame
from ..core.scene import Scene
from ..core import constants as C
from ..services.ui import Button
from .game_scene import GameScene

class MenuScene(Scene):
    def enter(self, **kwargs):
        cx, cy = C.WIDTH // 2, C.HEIGHT // 2
        self.btn = Button("Грати", (cx-100, cy-30, 200, 60),
                          on_click=lambda: self.app.change_scene(GameScene))

    def handle_events(self, events):
        self.btn.handle(events)

    def render(self, screen: pygame.Surface):
        self.btn.draw(screen)
