import pygame


class Block(pygame.sprite.Sprite):
    def __init__(self, pos, size=(32, 32), color=(180, 70, 40), solid=True, hp=50):
        super().__init__()
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=pos)
        self.solid = solid
        self.max_hp = hp
        self.hp = hp


    def take_damage(self, amount):
        if self.max_hp <= 0:
            return
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
