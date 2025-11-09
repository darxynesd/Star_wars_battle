"""
Основна сцена рівня: ініціалізує рівень (через systems/level_system.py), створює сутності (гравець, вороги, базу), реєструє системи (колізії, стрільба, AI). Обробляє паузу/перехід рівня/програш.
"""
import pygame
from ..core.scene import Scene
from ..core import constants as C
from ..systems.level_system import LevelSystem
from ..systems.collision_system import CollisionSystem
from ..systems.shooting_system import ShootingSystem
from ..systems.ai_system import AISystem
from .pause_scene import PauseScene

class GameScene(Scene):
    def enter(self, **kwargs):
        self.level = LevelSystem(self.app.assets)
        self.player, self.enemies, self.blocks, self.eagle, self.bounds = self.level.build()
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.bullets = pygame.sprite.Group()

        for b in self.blocks: self.all_sprites.add(b, layer=b.layer)
        for e in self.enemies: self.all_sprites.add(e, layer=e.layer)
        if self.eagle: self.all_sprites.add(self.eagle, layer=self.eagle.layer)
        self.all_sprites.add(self.player, layer=self.player.layer)

        self.collision = CollisionSystem(self.app.physics)
        self.shooting = ShootingSystem(self.app.assets)
        self.ai = AISystem(self.app.physics)
        self.font = pygame.font.SysFont("Arial", 28)

        self.state = "playing"      # playing / gameover / win
        self.timer = 0.0            # таймер після перемоги або поразки

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.app.change_scene(PauseScene, prev_scene=self)

    def update(self):
        dt = self.app.time.dt

        # якщо перемога або поразка — рахуємо таймер
        if self.state in ("gameover", "win"):
            self.timer += dt
            if self.timer > 2.0:      # через 2 секунди перезапуск
                self.enter()
            return

        # --- рух гравця ---
        v = self.player.handle_input(self.app.input)
        dx, dy = int(v.x * self.player.speed * dt), int(v.y * self.player.speed * dt)
        self.app.physics.move_and_collide(self.player, dx, dy, self.blocks)

        # межі карти
        if not self.bounds.contains(self.player.rect):
            if self.player.rect.left < self.bounds.left: self.player.rect.left = self.bounds.left
            if self.player.rect.right > self.bounds.right: self.player.rect.right = self.bounds.right
            if self.player.rect.top < self.bounds.top: self.player.rect.top = self.bounds.top
            if self.player.rect.bottom > self.bounds.bottom: self.player.rect.bottom = self.bounds.bottom

        # стрільба
        if self.app.input.pressed("fire"):
            self.shooting.player_try_shoot(self.player, self.bullets)

        # рух і стрільба ворогів
        self.ai.update(dt, self.enemies, self.blocks, self.bounds)
        for e in self.enemies:
            self.shooting.enemy_try_shoot(e, self.bullets)

        # апдейти куль
        for b in list(self.bullets): b.update(dt)

        # перевірка колізій
        self.collision.update(self.player, self.enemies, self.bullets, self.blocks, self.eagle, self._on_event)

        # умова перемоги 💪
        if len(self.enemies) == 0 and self.state == "playing":
            self.state = "win"
            self.timer = 0.0

        self.all_sprites.update(dt)

    def _on_event(self, name):
        if name == "eagle_down":
            self.state = "gameover"
            self.timer = 0.0
        elif name == "player_dead":
            self.state = "gameover"
            self.timer = 0.0

    def render(self, screen):
        self.all_sprites.draw(screen)
        for b in self.bullets:
            screen.blit(b.image, b.rect)

        # HP лічильник
        hp_text = self.font.render(f"HP: {self.player.hp}", True, (255, 255, 255))
        screen.blit(hp_text, (20, 20))

        # повідомлення про стан
        if self.state == "gameover":
            msg = self.font.render("GAME OVER", True, (255, 80, 80))
            screen.blit(msg, msg.get_rect(center=(C.WIDTH // 2, 50)))

        elif self.state == "win":
            msg = self.font.render("LEVEL CLEAR!", True, (100, 255, 100))
            screen.blit(msg, msg.get_rect(center=(C.WIDTH // 2, 50)))
