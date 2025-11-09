import pygame
from ..core import constants as C


class Base(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (230, 230, 100), (24, 24), 20)
        self.rect = self.image.get_rect(center=pos)
        self.max_hp = C.BASE_MAX_HP
        self.hp = self.max_hp
