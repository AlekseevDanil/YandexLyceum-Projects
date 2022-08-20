import pygame
# Игровые настройки
TITLE = "Bunny Jumper"
ICON_SURF = pygame.image.load("./images/BJ-icon.jpg")
WIDTH = 470
HEIGHT = 600
FPS = 60
NAME_FONT = 'bahnschrift'
HS_FILE = "highscore.txt"
HS_FILE_2 = "highscore_2.txt"
SPRITESHEET = "spritesheet_jumper.png"

# Свойства игрока
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 21

# Свойства в игре
BOOST = 70
POW_SPAWN_PCT = 7
MOB_FREQ = 5000
PLAYER_LAYER = 2
MOB_LAYER = 2
PLATFORM_LAYER = 1
POW_LAYER = 1
CLOUD_LAYER = 0

# Стартовая площадка
PLATFORM_LIST = [(0, HEIGHT - 60),
                 (WIDTH / 2 - 50, HEIGHT * 3 / 4 - 50),
                 (125, HEIGHT - 350),
                 (350, 200),
                 (175, 100)]

# Определение цветов
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
ORANGE = (255, 136, 0)
PURPLE = (148, 0, 211)
BGCOLORINGAME = (0, 200, 200)
BGCOLORINGAME_2 = (245, 152, 224)

# Картики предметов
BGCOLOR_FAIL = pygame.image.load('./images/background_failgame.png')
BGCOLOR = pygame.image.load('./images/background_main.png')
EXITBUTTON = pygame.image.load('./images/exit.png')
CONTINUE_GAME = pygame.image.load('./images/continue.png')
LITLE_LEFTUP_MENU = pygame.image.load(
    './images/litle_menu(exit-pause-restart).png')
PREV_NEXT_EXIT = pygame.image.load('./images/main_menu.png')
PREV_NEXT_EXIT_2 = pygame.image.load('./images/main_menu_2.png')
BGCOLOR_FAIL_2 = pygame.image.load('./images/background_failgame_2.png')
BGCOLOR_2 = pygame.image.load('./images/background_main_2.png')
