import pygame
from pygame.locals import *
from sys import exit
import configparser


"""constants"""
CONFIG = 'config.cfg'
# Window Resolution
SCREEN_MIN_X = 600      # min resolution should work on
SCREEN_MIN_Y = 400      # screen with 640x480 pixels
# Colors
BLUE = pygame.Color(30, 144, 255)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)
BLACK = pygame.Color(0, 0, 0)
BACKGROUND = pygame.Color(200, 200, 200)
GRAY = pygame.Color(100, 100, 100)
# Settings
CONF_DISPLAY = 'Display'
CONF_DISPLAY_WIDTH = 'width'
CONF_DISPLAY_HEIGHT = 'height'
CONF_DISPLAY_FULLSCREEN = 'fullscreen'
CONF_DISPLAY_FPS = 'fps'
"""global variables"""
game_is_running = None
screen = screen_x = screen_y = fps = fullscreen = None


def read_settings():
    """read the settings from config.cfg"""
    global screen_x, screen_y, fps, fullscreen
    try:
        config = configparser.RawConfigParser()
        config.read(CONFIG)

        """get display configuration"""
        screen_x = config.getint(CONF_DISPLAY, CONF_DISPLAY_WIDTH)
        screen_y = config.getint(CONF_DISPLAY, CONF_DISPLAY_HEIGHT)
        fps = config.getint(CONF_DISPLAY, CONF_DISPLAY_FPS)
        fullscreen = config.getboolean(CONF_DISPLAY, CONF_DISPLAY_FULLSCREEN)
    except configparser.NoSectionError:
        default_settings()
        read_settings()

    # controls
    # TODO

    # Audio
    # TODO


def write_settings():
    config = configparser.RawConfigParser()

    """write display configuration"""
    config.add_section(CONF_DISPLAY)
    config.set(CONF_DISPLAY, CONF_DISPLAY_WIDTH, screen_x)
    config.set(CONF_DISPLAY, CONF_DISPLAY_HEIGHT, screen_y)
    config.set(CONF_DISPLAY, CONF_DISPLAY_FPS, fps)
    config.set(CONF_DISPLAY, CONF_DISPLAY_FULLSCREEN, fullscreen)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def default_settings():
    config = configparser.RawConfigParser()

    """write default display configuration"""
    config.add_section(CONF_DISPLAY)
    config.set(CONF_DISPLAY, CONF_DISPLAY_WIDTH, 800)
    config.set(CONF_DISPLAY, CONF_DISPLAY_HEIGHT, 600)
    config.set(CONF_DISPLAY, CONF_DISPLAY_FPS, 25)
    config.set(CONF_DISPLAY, CONF_DISPLAY_FULLSCREEN, True)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def init_screen():
    """switch to fullscreen mode"""
    global screen, screen_x, screen_y, fullscreen
    screen_resolution = pygame.display.Info()
    s_width, s_height = screen_resolution.current_w, screen_resolution.current_h

    if fullscreen:
        screen_x, screen_y = s_width, s_height
        screen = pygame.display.set_mode((screen_x, screen_y), FULLSCREEN | HWSURFACE | DOUBLEBUF, 24)
    else:
        if s_width < screen_x:
            screen_x = s_width
        if s_height - 50 < screen_y - 50:    # leave some space for the menubar etc
            screen_y = s_height - 50
        screen = pygame.display.set_mode((screen_x, screen_y), HWSURFACE | DOUBLEBUF | RESIZABLE, 24)


def refresh_screen():
    """refresh the pygame screen/window"""
    screen.fill(BACKGROUND)
    pygame.display.update()


def quit_game():
    """quit the game"""
    pygame.quit()
    exit()


def init_game():
    """initialize the game variables"""
    global game_is_running
    # initialize the multidimensional array (list) and other global variables
    game_is_running = True
    read_settings()
    init_screen()


def start_game():
    """start the game"""
    global screen_x, screen_y, screen, fps
    # PyGame initialization
    pygame.init()
    init_game()
    clock = pygame.time.Clock()
    pygame.display.set_caption("pyRunner")
    refresh_counter = 0

    # init screen
    refresh_screen()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            elif event.type == VIDEORESIZE:
                screen_x, screen_y = event.dict['size']
                if screen_x < SCREEN_MIN_X:
                    screen_x = SCREEN_MIN_X
                if screen_y < SCREEN_MIN_Y:
                    screen_y = SCREEN_MIN_Y
                screen = pygame.display.set_mode((screen_x, screen_y), HWSURFACE | DOUBLEBUF | RESIZABLE, 24)
                # redraw the screen content with adjusted size
                refresh_screen()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    quit_game()
                if game_is_running:
                    if K_0 <= event.key <= K_9:
                        pass
                    if event.key == K_LEFT:
                        pass
                    if event.key == K_RIGHT:
                        pass
                    if event.key == K_SPACE or event.key == K_DOWN:
                        pass
                    # lazy update the screen, only if a key was pressed while the game is running
                    refresh_screen()
                else:
                    if event.key == K_n:
                        player_one_starts = True
                        init_game()
                    if event.key == K_r:
                        init_game()
            # in case the game board disappears after switching to full screen on macos x
            elif event.type == MOUSEBUTTONDOWN:
                if game_is_running:
                    refresh_screen()
                # x, y = pygame.mouse.get_pos()

        # save cpu resources
        clock.tick(fps)

        """
        update screen at least once every second

        seems like % is really slow
        replacing this with refresh_counter % fps is 0
        consumes 50% of one core from a 2,4 GHz Core i7
        just comparing values consumes ten times less (~5%)
        """
        if fps <= refresh_counter:
            refresh_screen()
            refresh_counter = 0
        else:
            refresh_counter += 1


# start the 4 in a row game
start_game()
