"""
Мапінг клавіш → дії (вліво/вправо/вогонь/пауза). Підтримка ремапу та геймпада.
"""
import pygame

DEFAULT_KEYS = {
    "left": pygame.K_LEFT,
    "right": pygame.K_RIGHT,
    "up": pygame.K_UP,
    "down": pygame.K_DOWN,
    "fire": pygame.K_SPACE,
    "pause": pygame.K_ESCAPE,
}

class Input:
    def __init__(self, mapping=None):
        self.map = mapping or DEFAULT_KEYS
        self.actions = {k: False for k in self.map}

    def update(self, events):
        pressed = pygame.key.get_pressed()
        for act, key in self.map.items():
            self.actions[act] = pressed[key]

    def pressed(self, action: str) -> bool:
        return self.actions.get(action, False)
