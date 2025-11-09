import pygame

from src.core.constants import GAME_OVER_EVENT


class CollisionSystem:
    def __init__(self, blocks, enemies, player, base, bullets, audio=None):
        self.blocks = blocks
        self.enemies = enemies
        self.player = player          # GroupSingle
        self.base = base              # GroupSingle
        self.bullets = bullets
        self.audio = audio

    def update(self):
        p = self.player.sprite
        b = self.base.sprite

        # --- кулі ---
        for bullet in list(self.bullets):
            # по блоках
            hit_blocks = pygame.sprite.spritecollide(bullet, self.blocks, False)
            if hit_blocks:
                for blk in hit_blocks:
                    if hasattr(blk, "take_damage"):
                        blk.take_damage(getattr(bullet, "damage", 25))
                bullet.kill()
                continue

            # по ворогах (тільки якщо куля гравця)
            if bullet.team == "player":
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, False)
                if hit_enemies:
                    for e in hit_enemies:
                        e.hp -= getattr(bullet, "damage", 25)
                        if e.hp <= 0:
                            e.kill()
                    bullet.kill()
                    continue

            # по гравцю/базі (тільки якщо куля ворога)
            if bullet.team == "enemy":
                if p and p.alive() and bullet.rect.colliderect(p.rect):
                    p.hp -= getattr(bullet, "damage", 25)
                    bullet.kill()
                    if p.hp <= 0:
                        p.kill()
                    continue
                if b and bullet.rect.colliderect(b.rect):
                    b.hp -= getattr(bullet, "damage", 25)
                    bullet.kill()
                    if b.hp <= 0:
                        b.kill()
                    continue

        # --- контактні колізії без урону ---
        # гравець ↔ вороги: більше НЕ наносимо урон, максимум — розсунути
        if p:
            collide = pygame.sprite.spritecollide(p, self.enemies, False)
            for e in collide:
                # простий розштовхувач: відкотити ворога на 1px у протилежний бік
                if hasattr(e, "direction"):
                    e.rect.x -= int(e.direction.x or 0)
                    e.rect.y -= int(e.direction.y or 0)

        # вороги ↔ база: без контактного урону (тільки кулі ворогів мають шкодити)
        # якщо хочеш повністю блокувати наскрізне проходження — можеш:
        if b:
            for e in pygame.sprite.spritecollide(b, self.enemies, False):
                # відкотити ворога з бази
                if hasattr(e, "direction"):
                    e.rect.x -= int(e.direction.x or 0)
                    e.rect.y -= int(e.direction.y or 0)
        if p and getattr(p, "hp", 1) <= 0:
            pygame.event.post(pygame.event.Event(GAME_OVER_EVENT, {"reason": "player"}))
        if b and getattr(b, "hp", 1) <= 0:
            pygame.event.post(pygame.event.Event(GAME_OVER_EVENT, {"reason": "base"}))