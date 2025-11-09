"""
Спільні UI-компоненти: кнопка, лейбл, панель життя/манти, віджети меню, повідомлення «PAUSE»
"""

import pygame

class Button:
    def __init__(self, text, rect, on_click):
        self.text = text
        self.rect = pygame.Rect(rect)
        self.on_click = on_click
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, surf):
        pygame.draw.rect(surf, (60, 60, 70), self.rect, border_radius=8)
        pygame.draw.rect(surf, (200, 200, 210), self.rect, 2, border_radius=8)
        txt = self.font.render(self.text, True, (230, 230, 240))
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle(self, events):
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.rect.collidepoint(e.pos):
                    self.on_click()

class UI:
    def __init__(self, assets):
        self.assets = assets
