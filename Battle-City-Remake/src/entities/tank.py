import pygame
from ..core import constants as C


class Tank(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.team = "player"
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (100, 200, 100), (4, 4, 32, 32), border_radius=8)
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(0, -1)
        self.speed = C.PLAYER_SPEED
        self.max_hp = C.PLAYER_MAX_HP
        self.hp = self.max_hp
        self.cooldown = 0.0
        self.fire_rate = 0.5

    def handle_movement(self, axis, dt):
        x, y = axis
        v = pygame.Vector2(x, y)
        if v.length_squared() > 0:
            v = v.normalize()
            self.direction = v
        self.rect.x += v.x * self.speed * dt
        self.rect.y += v.y * self.speed * dt

    def update(self, dt):
        if self.cooldown > 0:
            self.cooldown -= dt

    def can_shoot(self) -> bool:
        return self.cooldown <= 0

    def reset_cooldown(self):
        self.cooldown = self.fire_rate
