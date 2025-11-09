"""
Низькорівневі операції: AABB-колізії, рух з урахуванням тайлів (брик/стік), проникність об’єктів (куль), ковзання по льоду.
"""
import pygame

class Physics:
    @staticmethod
    def move_and_collide(sprite, dx, dy, blockers):
        """Просте AABB: рухаємо по осі X, колізія, потім по осі Y."""
        sprite.rect.x += dx
        hit_list = [b for b in blockers if sprite.rect.colliderect(b.rect)]
        for b in hit_list:
            if dx > 0: sprite.rect.right = b.rect.left
            elif dx < 0: sprite.rect.left = b.rect.right

        sprite.rect.y += dy
        hit_list = [b for b in blockers if sprite.rect.colliderect(b.rect)]
        for b in hit_list:
            if dy > 0: sprite.rect.bottom = b.rect.top
            elif dy < 0: sprite.rect.top = b.rect.bottom

    @staticmethod
    def rect_collision(a, b) -> bool:
        return a.rect.colliderect(b.rect)
