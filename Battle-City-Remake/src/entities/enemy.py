import pygame
from pygame import Vector2
from ..core import constants as C


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.direction = Vector2(0, 1)
        self.speed = 80
        self.team = "enemy"
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (200, 60, 60), (4, 4, 32, 32), border_radius=6)
        self.rect = self.image.get_rect(center=pos)
        self.direction = pygame.Vector2(0, 1)
        self.speed = C.ENEMY_SPEED
        self.hp = C.ENEMY_MAX_HP
        self.change_dir_cd = 0.0
        self.shoot_cd = 0.0

    def update(self, dt):
        screen_rect = pygame.display.get_surface().get_rect()
        if not screen_rect.contains(self.rect):
            if self.rect.left < 0: self.rect.left = 0; self.direction = pygame.Vector2(1, 0)
            if self.rect.right > screen_rect.width: self.rect.right = screen_rect.width; self.direction = pygame.Vector2(
                -1, 0)
            if self.rect.top < 0: self.rect.top = 0; self.direction = pygame.Vector2(0, 1)
            if self.rect.bottom > screen_rect.height: self.rect.bottom = screen_rect.height; self.direction = pygame.Vector2(
                0, -1)

