import pygame
from pygame.locals import *
import configparser


"""constants"""
CONFIG = "config.cfg"
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
_CONF_DISPLAY = "Display"
_CONF_DISPLAY_WIDTH = "width"
_CONF_DISPLAY_HEIGHT = "height"
_CONF_DISPLAY_FULLSCREEN = "fullscreen"
_CONF_DISPLAY_FPS = "fps"
"""global variables"""
game_is_running = None
screen = screen_x = screen_y = fps = fullscreen = None


@staticmethod
def _default_settings():
    config = configparser.RawConfigParser()

    """write default display configuration"""
    config.add_section(_CONF_DISPLAY)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH, 800)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT, 600)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FPS, 25)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN, True)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def read_settings():
    """read the settings from config.cfg"""
    global screen_x, screen_y, fps, fullscreen
    try:
        config = configparser.RawConfigParser()
        config.read(CONFIG)

        """get display configuration"""
        screen_x = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH)
        screen_y = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT)
        fps = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_FPS)
        fullscreen = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN)
    except configparser.NoSectionError:
        _default_settings()
        read_settings()

    # controls
    # TODO

    # Audio
    # TODO


def write_settings():
    config = configparser.RawConfigParser()

    """write display configuration"""
    config.add_section(_CONF_DISPLAY)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH, screen_x)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT, screen_y)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FPS, fps)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN, fullscreen)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def init_screen():
    """switch to fullscreen mode"""
    global screen, screen_x, screen_y, fullscreen
    screen_resolution = pygame.display.Info()
    s_width, s_height = screen_resolution.current_w, screen_resolution.current_h

    read_settings()

    if fullscreen:
        screen_x, screen_y = s_width, s_height
        screen = pygame.display.set_mode((screen_x, screen_y), FULLSCREEN | HWSURFACE | DOUBLEBUF, 24)
    else:
        if s_width < screen_x:
            screen_x = s_width
        if s_height - 50 < screen_y - 50:  # leave some space for the menubar etc
            screen_y = s_height - 50
        screen = pygame.display.set_mode((screen_x, screen_y), HWSURFACE | DOUBLEBUF | RESIZABLE, 24)


def refresh_screen():
    """refresh the pygame screen/window"""
    screen.fill(BACKGROUND)
    pygame.display.update()


def set_resolution(x, y):
    global screen, screen_x, screen_x
    if x < SCREEN_MIN_X:
        x = SCREEN_MIN_X
    if y < SCREEN_MIN_Y:
        y = SCREEN_MIN_Y
    screen = pygame.display.set_mode((x, y), HWSURFACE | DOUBLEBUF | RESIZABLE, 24)
    # redraw the screen content with adjusted size
    refresh_screen()


def get_screen():
    return screen


def get_fps():
    return fps
