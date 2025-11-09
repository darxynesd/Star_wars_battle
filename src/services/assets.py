"""
Сервіс завантаження/кешування ресурсів: читає resources.yaml, валідуючи наявність файлів; описує нотацію ключів і правила віддачі спрайтів/атласів/звуків/шрифтів.
"""
import os
import pygame

# Можеш підставити реальні шляхи:
IMAGE_PATHS = {
    # "images.tanks.player": "assets/images/tanks/player_idle.png",
}

COLORS = {
    "player": (70, 200, 90),
    "enemy": (220, 90, 70),
    "brick": (160, 70, 40),
    "steel": (120, 120, 130),
    "bush": (50, 140, 70),
    "ice": (170, 210, 240),
    "water": (40, 90, 160),
    "bullet": (250, 230, 90),
    "eagle": (200, 200, 200),
    "powerup": (240, 120, 240),
}

class Assets:
    def __init__(self):
        self._cache = {}

    def image(self, key: str, size=(32, 32), fallback_color=(200, 200, 200)) -> pygame.Surface:
        """Повертає Surface. Якщо в IMAGE_PATHS є шлях — завантажує; інакше робить кольорову заглушку."""
        if key in self._cache:
            return self._cache[key]
        path = IMAGE_PATHS.get(key)
        if path and os.path.exists(path):
            surf = pygame.image.load(path).convert_alpha()
        else:
            color = COLORS.get(key.split(".")[-1], fallback_color)
            surf = pygame.Surface(size, pygame.SRCALPHA)
            surf.fill(color)
        self._cache[key] = surf
        return surf

    def animation(self, key: str, frames: int, size=(32, 32)):
        """Повертає список кадрів-заглушок (для вибуху/анім.руху)."""
        return [self.image(key, size=size) for _ in range(frames)]
