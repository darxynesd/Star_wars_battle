import pygame


class GameClock:
    def __init__(self, target_fps: int = 60):
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.delta_time = 0.0

    def tick(self) -> float:
        self.delta_time = self.clock.tick(self.target_fps) / 1000.0
        return self.delta_time

    def get_fps(self) -> float:
        return self.clock.get_fps()
