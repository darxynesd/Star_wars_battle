"""
Гравець: швидкість, напрямок, анімація руху, перезарядка, обробка команд з input. Параметри беруться з config.settings. Приймає події «POWERUP_PICKED».
"""
import pygame
from .base import Entity
from ..core import constants as C

class Tank(Entity):
    def __init__(self, image, pos, speed=120, tag="player"):
        super().__init__(image, pos, layer=C.LAYER_ENTITIES, tag=tag)
        self.speed = speed
        self.reload = 0.4
        self._cooldown = 0.0
        self.direction = pygame.Vector2(0, -1)
        self.hp = 3

    def handle_input(self, inp):
        v = pygame.Vector2(0, 0)
        if inp.pressed("left"):  v.x -= 1
        if inp.pressed("right"): v.x += 1
        if inp.pressed("up"):    v.y -= 1
        if inp.pressed("down"):  v.y += 1
        if v.length_squared() > 0:
            self.direction = v.normalize()
        return v

    def take_damage(self, dmg=1):
        self.hp -= dmg
        if self.hp <= 0:
            self.alive = False

    def can_shoot(self) -> bool:
        return self._cooldown <= 0.0

    def shot_fired(self):
        self._cooldown = self.reload

    def update(self, dt):
        if self._cooldown > 0:
            self._cooldown -= dt
