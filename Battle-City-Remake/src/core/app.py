import pygame, traceback
from .time import GameClock
from .scene_manager import SceneManager
from . import constants as C
from .events import EventBus
from ..services.assets import ResourceManager
from ..services.audio import AudioManager
from ..services.input import InputManager
from ..services.physics import Physics
from ..services.save import load_game
from ..scenes.menu import MenuScene
from ..scenes.game import GameScene
from ..scenes.game_over import GameOverScene
from ..scenes.pause import PauseScene   # ← переконайся, що файл існує

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(C.WINDOW_SIZE)
        pygame.display.set_caption(C.TITLE)

        self.clock = GameClock(C.FPS)
        self.bus = EventBus()
        self.assets = ResourceManager()
        self.audio = AudioManager(self.assets)
        self.input = InputManager(C.KEYS)
        self.physics = Physics()
        self.save = load_game()

        self.scenes = SceneManager()
        services = {
            "bus": self.bus,
            "assets": self.assets,
            "audio": self.audio,
            "input": self.input,
            "physics": self.physics,
            "save": self.save,
        }
        self.scenes.register("menu", MenuScene(self.scenes, services))
        self.scenes.register("game", GameScene(self.scenes, services))
        self.scenes.register("pause", PauseScene(self.scenes, services))
        self.scenes.register("game_over", GameOverScene(self.scenes, services))
        self.scenes.change("menu")
        self.running = True

    def run(self):
        while self.running:
            try:
                dt = self.clock.tick()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        self.running = False
                    else:
                        self.scenes.current.handle_event(e)

                self.scenes.current.update(dt)
                self.scenes.current.draw(self.screen)
                pygame.display.flip()
            except Exception as ex:
                print("\n=== Uncaught exception in main loop ===")
                traceback.print_exc()
                # невелика пауза, щоб вікно не закрилось миттєво
                pygame.time.delay(1500)
                self.running = False

        pygame.quit()
