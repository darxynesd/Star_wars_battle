"""
Оверлей з варіантами «Продовжити», «Вийти в меню». Повертає керування в game_scene або робить перехід у menu_scene.
"""

import pygame
from ..core.scene import Scene

class PauseScene(Scene):
    def enter(self, **kwargs):
        self.prev = kwargs["prev_scene"]
        self.font = pygame.font.SysFont("Arial", 48)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.app.change_scene(type(self.prev))

    def render(self, screen):
        self.prev.render(screen)
        txt = self.font.render("PAUSE", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=(screen.get_width()//2, 100)))
