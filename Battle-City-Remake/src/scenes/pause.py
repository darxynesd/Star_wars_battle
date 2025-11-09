# game/scenes/pause.py
import pygame
from ..services.ui import Button

class PauseScene:
    def __init__(self, sm, services):
        self.sm = sm
        self.srv = services
        self.screen = pygame.display.get_surface()
        assets = self.srv["assets"]
        self.title_font = assets.font("ui_font")
        self.btn_font = assets.font("ui_font")

        w, h = self.screen.get_size()
        bw, bh = 260, 50
        cx = w // 2 - bw // 2
        cy = h // 2
        self.buttons = [
            Button((cx, cy - 40, bw, bh), "Продовжити", self._resume, self.btn_font),
            Button((cx, cy + 40, bw, bh), "В меню", self._to_menu, self.btn_font),
        ]

    def _resume(self):
        # повертаємось до попередньої сцени (див. push/pop нижче)
        self.sm.pop()

    def _to_menu(self):
        # викидаємо паузу і переходимо в меню
        self.sm.pop()         # прибрати паузу
        self.sm.change("menu")

    def enter(self): pass
    def exit(self): pass

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self._resume()
        for b in self.buttons:
            b.handle_event(e)

    def update(self, dt):
        # нічого не апдейтимо — все “заморожено”
        pass

    def draw(self, screen):
        # просто затемнюємо і малюємо UI поверх вже відрендереної GameScene
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        title = self.title_font.render("ПАУЗА", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100)))
        for b in self.buttons:
            b.draw(screen)
