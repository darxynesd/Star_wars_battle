import pygame
from ..entities.block import Block


class LevelSystem:
    def __init__(self, tile_size=32):
        self.tile_size = tile_size
        self.blocks = pygame.sprite.Group()
        self.tiles = pygame.sprite.Group()

    def load_demo_level(self, w=25, h=18):
        self.blocks.empty()
        # простенька рамка з цегли
        for x in range(w):
            self.blocks.add(Block((x * self.tile_size, 0)))
            self.blocks.add(Block((x * self.tile_size, (h - 1) * self.tile_size)))
        for y in range(h):
            self.blocks.add(Block((0, y * self.tile_size)))
            self.blocks.add(Block(((w - 1) * self.tile_size, y * self.tile_size)))

    def draw(self, screen):
        self.blocks.draw(screen)

    def check_collision(self, rect: pygame.Rect) -> bool:
        """
        Повертає True, якщо прямокутник впирається у непрохідний тайл.
        Вважаємо, що у тайла може бути атрибут .solid (за замовчанням True).
        """
        for tile in self.tiles:  # якщо у тебе self.blocks — заміни тут і в load_level()
            if getattr(tile, "solid", True) and tile.rect.colliderect(rect):
                return True
        return False
