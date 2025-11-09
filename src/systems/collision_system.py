"""
Єдине місце перевірки зіткнень між групами: кулі ↔ блоки, кулі ↔ танки, танки ↔ тайли, танки ↔ бонуси. Видає події «HIT_BRICK», «HIT_STEEL», «TANK_DAMAGED», «POWERUP_PICKED».
"""

from ..core import constants as C

class CollisionSystem:
    def __init__(self, physics):
        self.physics = physics

    def update(self, player, enemies, bullets, blocks, eagle, on_events):
        for b in list(bullets):
            # блоки
            for bl in list(blocks):
                if self.physics.rect_collision(b, bl):
                    bullets.remove(b); b.kill()
                    if bl.kind == "brick":
                        bl.hp -= 1
                        if bl.hp <= 0:
                            blocks.remove(bl); bl.kill()
                    return
            # вороги
            if b.owner_tag == "player":
                for e in list(enemies):
                    if self.physics.rect_collision(b, e):
                        enemies.remove(e); e.kill()
                        bullets.remove(b); b.kill()
                        return
            else:
                # ворожа куля потрапила в гравця
                if self.physics.rect_collision(b, player):
                    bullets.remove(b); b.kill()
                    player.take_damage(1)
                    if not player.alive:
                        on_events("player_dead")
                    return
            # база
            if eagle and self.physics.rect_collision(b, eagle):
                bullets.remove(b); b.kill()
                on_events("eagle_down")
                return
