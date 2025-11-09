import pygame, sys
from ..services.ui import Button

class MenuScene:
    def __init__(self, sm, services):
        self.sm = sm
        self.services = services
        self.screen = pygame.display.get_surface()
        assets = self.services["assets"]
        self.title_font = assets.font("big_font")
        self.btn_font = assets.font("ui_font")
        w, h = self.screen.get_size()
        bw, bh = 300, 60
        cx = w//2 - bw//2
        cy = h//2 - 100

        # УВАГА: Play -> change("game"), Exit -> quit
        self.buttons = [
            Button((cx, cy, bw, bh), "Грати", lambda: self.sm.change("game"), self.btn_font),
            Button((cx, cy+80, bw, bh), "Налаштування", lambda: None, self.btn_font),
            Button((cx, cy+160, bw, bh), "Вийти", self._exit_game, self.btn_font),
        ]

    def _exit_game(self):
        pygame.quit()
        sys.exit()

    def enter(self):
        # не падаємо, якщо mixer недоступний
        try:
            self.services["audio"].play_music("menu_music")
        except Exception:
            pass

    def exit(self): pass

    def handle_event(self, e):
        for b in self.buttons:
            b.handle_event(e)

    def update(self, dt):
        self.services["input"].update()

    def draw(self, screen):
        screen.fill((14, 16, 22))
        title = self.title_font.render("TANK BATTLE", True, (240,240,255))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, 150)))
        for b in self.buttons:
            b.draw(screen)
