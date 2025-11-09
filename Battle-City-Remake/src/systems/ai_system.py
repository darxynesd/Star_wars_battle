# systems/ai_system.py
import pygame, random
from pygame import Vector2

class AISystem:
    def __init__(self, enemies, level_system, shooting_system):
        self.enemies = enemies
        self.level_system = level_system
        self.shooting_system = shooting_system
        self.change_dir_time = 1000  # мс
        self._screen_rect = pygame.display.get_surface().get_rect()

    def update(self, dt, base_rect=None, player_rect=None):
        now = pygame.time.get_ticks()
        for enemy in self.enemies:
            # 1) періодична зміна напряму
            if not hasattr(enemy, "last_change") or now - enemy.last_change > self.change_dir_time:
                enemy.last_change = now
                # якщо є база — 70% наводимось у її бік, інакше випадково
                if base_rect and random.random() < 0.7:
                    self._aim_enemy(enemy, base_rect.center)
                else:
                    enemy.direction = random.choice([Vector2(1,0), Vector2(-1,0), Vector2(0,1), Vector2(0,-1)])

            # 2) рух із dt
            self._move_enemy(enemy, dt)

            # 3) рідкі постріли у бік напряму
            if random.random() < 0.015:
                self.shooting_system.shoot(enemy)

    def _aim_enemy(self, enemy, target_pos):
        v = Vector2(target_pos) - Vector2(enemy.rect.center)
        if v.length_squared() == 0:
            enemy.direction = Vector2(0,1)
        else:
            v = v.normalize()
            # квантові напрями 4-х напрямків
            if abs(v.x) > abs(v.y):
                enemy.direction = Vector2(1,0) if v.x > 0 else Vector2(-1,0)
            else:
                enemy.direction = Vector2(0,1) if v.y > 0 else Vector2(0,-1)

    def _move_enemy(self, enemy, dt):
        from pygame import Vector2
        d = getattr(enemy, "direction", Vector2(0, 1))
        if d.length_squared() == 0:
            d = Vector2(0, 1)
        speed = getattr(enemy, "speed", 80)
        move = d * speed * dt
        new_rect = enemy.rect.move(move.x, move.y)

        # кордони екрана (кламп + легкий поштовх всередину)
        if not self._screen_rect.contains(new_rect):
            if new_rect.left < self._screen_rect.left:
                new_rect.left = self._screen_rect.left
                enemy.direction = Vector2(1, 0);
                new_rect.x += 2
            if new_rect.right > self._screen_rect.right:
                new_rect.right = self._screen_rect.right
                enemy.direction = Vector2(-1, 0);
                new_rect.x -= 2
            if new_rect.top < self._screen_rect.top:
                new_rect.top = self._screen_rect.top
                enemy.direction = Vector2(0, 1);
                new_rect.y += 2
            if new_rect.bottom > self._screen_rect.bottom:
                new_rect.bottom = self._screen_rect.bottom
                enemy.direction = Vector2(0, -1);
                new_rect.y -= 2

        # безпечний виклик перевірки тайлів
        collides = False
        if hasattr(self.level_system, "check_collision"):
            collides = self.level_system.check_collision(new_rect)

        if not collides:
            enemy.rect = new_rect
        else:
            enemy.direction *= -1
            enemy.last_change = pygame.time.get_ticks()
