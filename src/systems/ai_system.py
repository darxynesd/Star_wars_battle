"""
Прості вороги: випадкові повороти, уникнення стіни, прицільний вогонь якщо на одній лінії, таймери прийняття рішень.
"""
class AISystem:
    def __init__(self, physics):
        self.physics = physics

    def update(self, dt, enemies, blocks, bounds):
        for e in enemies:
            e.decide(dt)
            dx = int(e.dir.x * e.speed * dt)
            dy = int(e.dir.y * e.speed * dt)
            self.physics.move_and_collide(e, dx, dy, blocks)

            # не виходити за межі карти
            if not bounds.contains(e.rect):
                if e.rect.left < bounds.left: e.rect.left = bounds.left
                if e.rect.right > bounds.right: e.rect.right = bounds.right
                if e.rect.top < bounds.top: e.rect.top = bounds.top
                if e.rect.bottom > bounds.bottom: e.rect.bottom = bounds.bottom
