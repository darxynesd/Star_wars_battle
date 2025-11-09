import pygame
from ..entities.bullet import Bullet


class ShootingSystem:
    def __init__(self, bullets_group, audio=None):
        self.bullets = bullets_group
        self.audio = audio

    def shoot(self, shooter):
        # якщо є перезарядка — поважаємо її
        if hasattr(shooter, "can_shoot") and not shooter.can_shoot():
            return
        direction = getattr(shooter, "direction", pygame.Vector2(0, -1))
        pos = (shooter.rect.centerx + direction.x * 24,
               shooter.rect.centery + direction.y * 24)
        team = getattr(shooter, "team", "player")  # ← фракція зі стрільця
        b = Bullet(pos, direction, team=team)
        self.bullets.add(b)
        if hasattr(shooter, "reset_cooldown"):
            shooter.reset_cooldown()
        if self.audio:
            self.audio.play_sfx("fire")
