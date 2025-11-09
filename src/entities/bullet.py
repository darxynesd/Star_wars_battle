"""
Снаряд: швидкість, джерело (гравець/ворог), правила зіткнень із блоками й танками, породження ефекту вибуху.
"""
import pygame
from .base import Entity
from ..core import constants as C

class Bullet(Entity):
    def __init__(self, image, pos, direction, speed=300, owner_tag="player"):
        super().__init__(image, pos, layer=C.LAYER_BULLETS, tag="bullet")
        self.dir = pygame.Vector2(direction)
        self.speed = speed
        self.owner_tag = owner_tag

    def update(self, dt):
        self.rect.x += int(self.dir.x * self.speed * dt)
        self.rect.y += int(self.dir.y * self.speed * dt)
