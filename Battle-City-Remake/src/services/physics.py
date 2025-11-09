import pygame


class Physics:

    @staticmethod
    def clamp_rect_to_screen(rect: pygame.Rect, screen: pygame.Surface):
        rect.clamp_ip(screen.get_rect())

    @staticmethod
    def aabb_overlap(a: pygame.Rect, b: pygame.Rect) -> bool:
        return a.colliderect(b)
