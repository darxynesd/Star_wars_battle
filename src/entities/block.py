"""
Тайлові перешкоди: тип (цегла/сталь/кущ/лід/вода), міцність, руйнування від куль.
"""
from .base import Entity
from ..core import constants as C

class Block(Entity):
    def __init__(self, image, pos, kind="brick", hp=1, solid=True):
        super().__init__(image, pos, layer=C.LAYER_TILES, tag="block")
        self.kind = kind
        self.hp = hp
        self.solid = solid
