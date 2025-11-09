import pygame
from ..entities.tank import Tank
from ..entities.enemy import Enemy
from ..entities.base import Base
from ..systems.level_system import LevelSystem
from ..systems.collision_system import CollisionSystem
from ..systems.shooting_system import ShootingSystem
from ..systems.ai_system import AISystem
from ..core import constants as C
import traceback

class GameScene:
    def __init__(self, sm, services):
        self.sm = sm
        self.srv = services
        self.screen = pygame.display.get_surface()
        assets = self.srv["assets"]
        try:
            self.font = assets.font("ui_font")
        except Exception:
            self.font = pygame.font.Font(None, 24)

        self.players = pygame.sprite.GroupSingle()
        self.enemies = pygame.sprite.Group()
        self.blocks = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.base = pygame.sprite.GroupSingle()

        self.level = LevelSystem()
        self.shooting = ShootingSystem(self.bullets, audio=self.srv.get("audio"))
        self.ai = AISystem(self.enemies, self.level, self.shooting)

        self.collisions = CollisionSystem(self.blocks, self.enemies, self.players, self.base, self.bullets, audio=self.srv.get("audio"))

    def enter(self):
        try:
            self.level.load_demo_level()
            self.blocks = self.level.blocks

            self.players.add(Tank((C.WINDOW_SIZE[0]//2, C.WINDOW_SIZE[1]-100)))
            self.base.add(Base((C.WINDOW_SIZE[0]//2, C.WINDOW_SIZE[1]-60)))
            for i in range(3):
                self.enemies.add(Enemy((100 + i*150, 120)))
        except Exception:
            print("GameScene.enter() failed:")
            traceback.print_exc()
            # повертаємо у меню, щоб не падало в нуль
            self.sm.change("menu")

    def exit(self):
        self.players.empty(); self.enemies.empty(); self.blocks.empty(); self.bullets.empty(); self.base.empty()

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.sm.push("pause")
        elif e.type == pygame.USEREVENT and getattr(e, "type", "") == "GAME_OVER":
            self.sm.change("game_over")  # перехід у сцену програшу

    def update(self, dt):
        self.srv["input"].update()
        p = self.players.sprite
        if p:
            p.handle_movement(self.srv["input"].move_axis(), dt)
            p.update(dt)
            if self.srv["input"].action("FIRE"):
                self.shooting.shoot(p)
        self.enemies.update(dt)
        self.bullets.update(dt)
        self.ai.update(dt)
        self.collisions.update()
        if p:
            p.rect.clamp_ip(self.screen.get_rect())
        base_rect = self.base.sprite.rect if self.base.sprite else None
        player_rect = self.players.sprite.rect if self.players.sprite else None
        self.ai.update(dt, base_rect=base_rect, player_rect=player_rect)
        self.collisions.update()

    def draw(self, screen):
        screen.fill((20, 20, 30))
        self.level.draw(screen)
        self.enemies.draw(screen)
        self.bullets.draw(screen)
        if self.base.sprite:
            screen.blit(self.base.sprite.image, self.base.sprite.rect)
        if self.players.sprite:
            screen.blit(self.players.sprite.image, self.players.sprite.rect)
            txt = self.font.render(f"HP: {self.players.sprite.hp}", True, (255,255,255))
            screen.blit(txt, (10, 10))
