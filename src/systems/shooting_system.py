"""
Правила стрільби: контроль перезарядки, створення кулі, звуки/ефекти при пострілі, обмеження «1 куля на екрані» для базового танка.
"""

import pygame
from ..entities.bullet import Bullet

class ShootingSystem:
    def __init__(self, assets):
        self.assets = assets

    def player_try_shoot(self, player, bullets_group):
        if player.can_shoot():
            img = self.assets.image("bullet", size=(8, 8))
            pos = player.rect.center
            b = Bullet(img, (pos[0]-4, pos[1]-4), player.direction, owner_tag="player")
            bullets_group.add(b)
            player.shot_fired()

    def enemy_try_shoot(self, enemy, bullets_group):
        if enemy.can_shoot():
            img = self.assets.image("bullet", size=(8, 8))
            pos = enemy.rect.center
            b = Bullet(img, (pos[0]-4, pos[1]-4), enemy.dir, owner_tag="enemy")
            bullets_group.add(b)
            enemy.shot_fired()
