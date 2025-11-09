import pygame
import random

class EagleBase(pygame.sprite.Sprite):
    """
    Головна база (Eagle). Якщо її знищено — гра програна.
    Має власну анімацію, здоров’я, ефекти вибуху.
    """

    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=pos)
        self.max_hp = 100
        self.hp = self.max_hp
        self.alive = True
        self.flash_timer = 0
        self.exploding = False
        self.explosion_timer = 0
        self._draw_eagle()

    # -------------------------------------------------------
    def _draw_eagle(self, damaged=False):
        """Малює орла — залежно від стану."""
        surf = self.image
        surf.fill((0, 0, 0, 0))
        center = surf.get_rect().center

        # Тіло
        color = (230, 230, 100) if not damaged else (180, 100, 50)
        pygame.draw.circle(surf, color, center, 20)

        # Крила
        pygame.draw.polygon(surf, (240, 240, 240),
                            [(5, 25), (15, 10), (23, 20)])
        pygame.draw.polygon(surf, (240, 240, 240),
                            [(43, 25), (33, 10), (25, 20)])

        # Очі
        pygame.draw.circle(surf, (0, 0, 0), (18, 20), 3)
        pygame.draw.circle(surf, (0, 0, 0), (30, 20), 3)

        # Дзьоб
        pygame.draw.polygon(surf, (255, 180, 60),
                            [(24, 26), (28, 26), (26, 34)])

        # Контур
        pygame.draw.circle(surf, (80, 60, 0), center, 22, 2)

    # -------------------------------------------------------
    def take_damage(self, amount):
        """Отримує шкоду."""
        if not self.alive:
            return

        self.hp -= amount
        self.flash_timer = 0.15
        print(f"🦅 Базі нанесено {amount} шкоди. HP: {self.hp}/{self.max_hp}")

        if self.hp <= 0:
            self.destroy()
        else:
            self._draw_eagle(damaged=True)

    # -------------------------------------------------------
    def destroy(self):
        """Знищення бази — починається вибух."""
        if self.exploding:
            return
        print("💥 Базу знищено! Кінець гри!")
        self.alive = False
        self.exploding = True
        self.explosion_timer = 1.2

    # -------------------------------------------------------
    def update(self, dt):
        """Оновлення ефектів — блиск, вибух."""
        if not self.alive and not self.exploding:
            return

        if self.flash_timer > 0:
            self.flash_timer -= dt
            if int(self.flash_timer * 20) % 2 == 0:
                self.image.fill((255, 0, 0, 60), special_flags=pygame.BLEND_RGBA_ADD)
        elif self.hp > 0:
            self._draw_eagle()

        if self.exploding:
            self.explosion_timer -= dt
            radius = random.randint(20, 40)
            boom = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
            pygame.draw.circle(boom, (255, random.randint(100,200), 0, 180),
                               (radius, radius), radius)
            boom_rect = boom.get_rect(center=self.rect.center)
            pygame.display.get_surface().blit(boom, boom_rect)

            if self.explosion_timer <= 0:
                self.kill()

    # -------------------------------------------------------
    def draw(self, surface):
        """Малює орла (і якщо знищено — дим)."""
        if self.alive:
            surface.blit(self.image, self.rect)
        else:
            smoke = pygame.Surface((50, 50), pygame.SRCALPHA)
            for i in range(6):
                c = 150 + random.randint(-20, 20)
                pygame.draw.circle(smoke, (c, c, c, 120),
                                   (random.randint(10, 40), random.randint(10, 40)),
                                   random.randint(4, 10))
            surface.blit(smoke, self.rect)
