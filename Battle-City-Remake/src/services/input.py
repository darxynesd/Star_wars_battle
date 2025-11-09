import pygame


_KEY_NAME_TO_K = {
    "w": pygame.K_w,
    "a": pygame.K_a,
    "s": pygame.K_s,
    "d": pygame.K_d,
    "space": pygame.K_SPACE,
    "escape": pygame.K_ESCAPE,
}


class InputManager:
    def __init__(self, logical_map):
        pygame.joystick.init()
        self.joy = pygame.joystick.Joystick(0) if pygame.joystick.get_count() else None
        if self.joy:
            self.joy.init()

        # логічні дії → pygame key
        self.key_map = {
            act: _KEY_NAME_TO_K.get(name, pygame.K_UNKNOWN)
            for act, name in logical_map.items()
        }
        self._keys = None

    def update(self):
        self._keys = pygame.key.get_pressed()

    def action(self, name: str) -> bool:
        k = self.key_map.get(name)
        return bool(self._keys and k != pygame.K_UNKNOWN and self._keys[k])

    def move_axis(self):
        x = float(self.action("RIGHT")) - float(self.action("LEFT"))
        y = float(self.action("DOWN")) - float(self.action("UP"))

        if self.joy:
            ax = self.joy.get_axis(0)
            ay = self.joy.get_axis(1)
            if abs(ax) > 0.3:
                x = ax
            if abs(ay) > 0.3:
                y = ay

        return x, y
