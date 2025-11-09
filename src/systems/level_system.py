"""
Завантаження/побудова рівня з data/levels/*.txt: парсинг символів у тайли/спавн-поінти, ресет сцени при програші/перемозі, перехід на наступний рівень.
"""
import pygame
from ..core import constants as C
from ..entities.block import Block
from ..entities.eagle_base import EagleBase
from ..entities.enemy import Enemy
from ..entities.tank import Tank

LEVEL_MAP = [
    "##########################",
    "#......E..............E..#",
    "#..####....####....####..#",
    "#........................#",
    "#..####....####....####..#",
    "#........................#",
    "#..####....####....####..#",
    "#........................#",
    "#........P..............#@",
    "##########################",
]

SYMBOLS = {
    "#": ("brick", 1, True),
    "@": ("eagle", 0, False),
    "E": ("enemy", 0, False),
    "P": ("player", 0, False),
    ".": None,
}

class LevelSystem:
    def __init__(self, assets):
        self.assets = assets

    def build(self):
        blocks = pygame.sprite.Group()
        enemies = pygame.sprite.Group()
        player = None
        eagle = None

        map_width = len(LEVEL_MAP[0]) * C.TILE
        map_height = len(LEVEL_MAP) * C.TILE
        offset_x = (C.WIDTH - map_width) // 2
        offset_y = (C.HEIGHT - map_height) // 2

        for y, row in enumerate(LEVEL_MAP):
            for x, ch in enumerate(row):
                info = SYMBOLS.get(ch)
                if not info:
                    continue
                kind, hp, solid = info
                px, py = offset_x + x * C.TILE, offset_y + y * C.TILE
                if kind == "brick":
                    img = self.assets.image("brick", size=(C.TILE, C.TILE))
                    blocks.add(Block(img, (px, py), kind="brick", hp=hp, solid=solid))
                elif kind == "eagle":
                    img = self.assets.image("eagle", size=(C.TILE, C.TILE))
                    eagle = EagleBase(img, (px, py))
                elif kind == "enemy":
                    img = self.assets.image("enemy", size=(C.TILE, C.TILE))
                    enemies.add(Enemy(img, (px, py)))
                elif kind == "player":
                    img = self.assets.image("player", size=(C.TILE, C.TILE))
                    player = Tank(img, (px, py))

        # межі карти
        bounds = pygame.Rect(offset_x, offset_y, map_width, map_height)
        return player, enemies, blocks, eagle, bounds
