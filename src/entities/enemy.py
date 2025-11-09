"""
Ворог: характеристики, що можуть відрізнятися (швидкий/важкий), реакція на AI-команди, таблиця станів (патруль, переслідування, стрільба).
"""
import random
import pygame
from .base import Entity
from ..core import constants as C

DIRECTIONS = [
    pygame.Vector2(1, 0),
    pygame.Vector2(-1, 0),
    pygame.Vector2(0, 1),
    pygame.Vector2(0, -1),
]

class Enemy(Entity):
    def __init__(self, image, pos, speed=90):
        super().__init__(image, pos, layer=C.LAYER_ENTITIES, tag="enemy")
        self.speed = speed
        self.dir = pygame.Vector2(0, 1)
        self.turn_cd = 0.0
        self.reload = 1.0
        self.cool = 0.0

    def decide(self, dt):
        self.turn_cd -= dt
        if self.turn_cd <= 0:
            self.turn_cd = random.uniform(0.7, 1.6)
            self.dir = random.choice(DIRECTIONS)  # ← тепер завжди Vector2

        self.cool = max(0.0, self.cool - dt)

    def can_shoot(self) -> bool:
        return self.cool <= 0

    def shot_fired(self):
        self.cool = self.reload
