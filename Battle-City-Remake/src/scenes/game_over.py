# scenes/game_over.py
import pygame
from ..services.ui import Button

class GameOverScene:
    def __init__(self, sm, services):
        self.sm = sm
        self.srv = services
        self.screen = pygame.display.get_surface()
        assets = self.srv["assets"]
        self.title_font = assets.font("big_font")
        self.btn_font = assets.font("ui_font")

        w, h = self.screen.get_size()
        bw, bh = 300, 60
        cx = w//2 - bw//2
        cy = h//2 + 40
        self.btn_menu = Button((cx, cy, bw, bh), "в меню", self._to_menu, self.btn_font)

    def _to_menu(self):
        self.sm.change("menu")

    def enter(self): pass
    def exit(self): pass

    def handle_event(self, e):
        self.btn_menu.handle_event(e)
        if e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN:
            self._to_menu()

    def update(self, dt): pass

    def draw(self, screen):
        screen.fill((10, 10, 16))
        title = self.title_font.render("гра програна", True, (255, 80, 80))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 60)))
        self.btn_menu.draw(screen)
