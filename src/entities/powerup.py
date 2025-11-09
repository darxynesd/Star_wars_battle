"""
Бонуси: щит, апґрейд кулі, заморозка ворогів, додаткове життя. Тривалі/миттєві ефекти, обробка через event_bus.
"""

from .base import Entity
from ..core import constants as C

class PowerUp(Entity):
    def __init__(self, image, pos, kind="shield"):
        super().__init__(image, pos, layer=C.LAYER_ENTITIES, tag="powerup")
        self.kind = kind
