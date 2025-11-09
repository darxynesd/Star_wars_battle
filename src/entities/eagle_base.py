"""
База, яку треба захищати. Стан «ціла/знищена», тригер програшу при руйнуванні.
"""

from .base import Entity
from ..core import constants as C

class EagleBase(Entity):
    def __init__(self, image, pos):
        super().__init__(image, pos, layer=C.LAYER_TILES, tag="eagle")
        self.alive_flag = True
