#Опис усіх налаштувань, що читаються при старті: розмір вікна, FPS-ліміт, початкові життя, швидкість танків/куль, мапа клавіш.
import core.constants as const
WINDOW_SIZE = (800, 600)
FPS = 60

INITIAL_LIVES = 3
TANK_SPEED = 4
BULLET_SPEED = 10

ENEMY_SPEED = 2

KEY_MAP = {
    "UP": const.KEY_MOVE_FORWARD,
    "DOWN": const.KEY_MOVE_BACKWARD,
    "LEFT": const.KEY_MOVE_LEFT,
    "RIGHT": const.KEY_MOVE_RIGHT,
    "FIRE": const.KEY_FIRE
}
