import pygame


class Button:
    def __init__(self, rect, text, on_click, font=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.hovered = False
        self.font = font or pygame.font.Font(None, 32)

    def handle_event(self, e: pygame.event.Event):
        if e.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(e.pos)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if self.hovered and self.on_click:
                self.on_click()

    def draw(self, screen: pygame.Surface):
        color = (40, 180, 200) if self.hovered else (30, 140, 160)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, width=2, border_radius=10)
        txt = self.font.render(self.text, True, (240, 240, 240))
        screen.blit(txt, txt.get_rect(center=self.rect.center))
