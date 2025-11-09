import pygame
from ..core import constants as C

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction: pygame.Vector2, color=(255, 220, 100), damage=25, team="player"):
        super().__init__()
        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (4, 4), 4)
        self.rect = self.image.get_rect(center=pos)
        self.dir = pygame.Vector2(direction)
        if self.dir.length_squared() == 0:
            self.dir.update(0, -1)
        else:
            self.dir = self.dir.normalize()
        self.speed = C.BULLET_SPEED
        self.damage = damage
        self.team = team            # ← фракція: "player" або "enemy"
        self.lifetime = 2.5

    def update(self, dt: float):
        move = self.dir * self.speed * dt
        self.rect.x += move.x
        self.rect.y += move.y
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
        screen = pygame.display.get_surface()
        if screen and not screen.get_rect().colliderect(self.rect):
            self.kill()
