"""
«Компонозитор» застосунку: ініціалізує Pygame, створює сервіси (Assets, Audio, Input, UI, Physics), шину подій, менеджер сцен; запускає головний цикл (tick → handle_input → update → render).
Патерн: Application/Composition Root + Game Loop.
Використання: імпортується в run.py, де створюється екземпляр App і викликається метод запуску.
"""

import pygame
from . import constants as C
from .time import Time
from .event_bus import EventBus
from ..services.assets import Assets
from ..services.audio import Audio
from ..services.input import Input
from ..services.physics import Physics
from ..services.ui import UI
from ..scenes.menu_scene import MenuScene

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT))
        pygame.display.set_caption(C.TITLE)
        self.clock = pygame.time.Clock()
        self.time = Time()
        self.bus = EventBus()
        self.assets = Assets()
        self.audio = Audio()
        self.input = Input()
        self.physics = Physics()
        self.ui = UI(self.assets)
        self.running = True
        self.scene = MenuScene(self)
        self.scene.enter()

    def run(self):
        while self.running:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.running = False

            self.input.update(events)
            self.scene.handle_events(events)

            self.time.update(self.clock)
            self.scene.update()

            self.screen.fill((20, 20, 24))
            self.scene.render(self.screen)
            pygame.display.flip()
            self.clock.tick(C.FPS)

        pygame.quit()

    def change_scene(self, scene_cls, **kwargs):
        self.scene.exit()
        self.scene = scene_cls(self)
        self.scene.enter(**kwargs)
