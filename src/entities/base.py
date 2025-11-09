"""
Спільні поля та поведінки для всіх ігрових об’єктів: позиція, розмір, шар рендеру, життєвий цикл (активний/видимий), доступ до сервісів, підписка на події.
"""
import pygame
from ..core import constants as C

class Entity(pygame.sprite.Sprite):
    def __init__(self, image, pos, layer=C.LAYER_ENTITIES, tag="entity"):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)
        self.tag = tag
        self.layer = layer
        self.alive = True

    def update(self, dt): ...
