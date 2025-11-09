import pygame
import random
import math

class PowerUp(pygame.sprite.Sprite):
    """
    Підсилення для гравця або ворога.
    Типи: heal, speed, shield, damage.
    Зникає через певний час або після підбору.
    """

    COLORS = {
        "heal": (120, 255, 120),
        "speed": (120, 180, 255),
        "shield": (255, 230, 100),
        "damage": (255, 100, 100),
    }

    ICONS = {
        "heal": "+",
        "speed": "⚡",
        "shield": "🛡️",
        "damage": "💥"
    }

    def __init__(self, pos, ptype=None):
        super().__init__()
        self.type = ptype or random.choice(list(self.COLORS.keys()))
        self.color = self.COLORS[self.type]
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.spawn_y = pos[1]
        self.timer = 10.0  # час життя (секунд)
        self.bounce = 0.0
        self.glow_phase = 0
        self._draw_powerup()

    # ---------------------------------------------------------
    def _draw_powerup(self):
        """Малює коло з блиском і іконкою."""
        surf = self.image
        surf.fill((0, 0, 0, 0))
        pygame.draw.circle(surf, self.color, (15, 15), 12)
        pygame.draw.circle(surf, (255, 255, 255), (15, 15), 13, 2)

        font = pygame.font.Font(None, 26)
        icon = self.ICONS.get(self.type, "?")
        text = font.render(icon, True, (0, 0, 0))
        rect = text.get_rect(center=(15, 15))
        surf.blit(text, rect)

    # ---------------------------------------------------------
    def update(self, dt):
        """Анімація блиску, підстрибування та таймер зникнення."""
        self.timer -= dt
        if self.timer <= 0:
            self.kill()
            return

        # підстрибування
        self.bounce += dt * 6
        offset = math.sin(self.bounce) * 5
        self.rect.centery = self.spawn_y + offset

        # блиск
        self.glow_phase += dt * 6
        glow_alpha = int((math.sin(self.glow_phase) * 0.5 + 0.5) * 100)
        glow = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, glow_alpha), (15, 15), 14)
        self.image.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    # ---------------------------------------------------------
    def apply(self, target):
        """
        Застосовує ефект до об'єкта (наприклад, Player або Enemy).
        target повинен мати властивості hp, speed, damage тощо.
        """
        if self.type == "heal":
            if hasattr(target, "hp"):
                target.hp = min(target.max_hp, target.hp + 30)
                print("💖 Здоров’я відновлено!")

        elif self.type == "speed":
            if hasattr(target, "speed"):
                target.speed *= 1.3
                print("⚡ Швидкість збільшено!")

        elif self.type == "shield":
            if hasattr(target, "shield_timer"):
                target.shield_timer = 5.0
                print("🛡️ Активовано щит!")

        elif self.type == "damage":
            if hasattr(target, "damage_boost"):
                target.damage_boost = 1.5
                print("💥 Підсилено атаку!")

        self.kill()  # зникає після підбору

    # ---------------------------------------------------------
    def draw(self, surface):
        """Малює підсилення."""
        surface.blit(self.image, self.rect)
