TITLE = "Battle City (Prototype)"
WIDTH, HEIGHT = 832, 768         # 26x24 тайлів ~32px
FPS = 60
TILE = 32

# шари рендера (від меншого до більшого)
LAYER_BG = 0
LAYER_TILES = 1
LAYER_ENTITIES = 2
LAYER_BULLETS = 3
LAYER_UI = 10

# групи колізій (просто мітки)
GROUP_PLAYER = "player"
GROUP_ENEMY = "enemy"
GROUP_BULLET = "bullet"
GROUP_BLOCK = "block"
GROUP_POWERUP = "powerup"
GROUP_EAGLE = "eagle"
