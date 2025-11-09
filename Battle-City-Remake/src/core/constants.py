import pygame
GAME_OVER_EVENT = pygame.USEREVENT + 1

TITLE = "TANK BATTLE"
WINDOW_SIZE = (800, 600)
FPS = 60

INITIAL_LIVES = 3
PLAYER_SPEED = 180
ENEMY_SPEED = 80
BULLET_SPEED = 400
PLAYER_MAX_HP = 120
ENEMY_MAX_HP = 100
BASE_MAX_HP = 100

KEYS = {
    "UP": "w",
    "DOWN": "s",
    "LEFT": "a",
    "RIGHT": "d",
    "FIRE": "space",
    "PAUSE": "escape",
}
