import pygame
from pygame.locals import *
import configparser


"""constants"""
NAME="pyRunner"
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
_CONF_INFO = "Info"
_CONF_INFO_NAME = "Name"
_CONF_DISPLAY = "Display"
_CONF_DISPLAY_WIDTH = "width"
_CONF_DISPLAY_HEIGHT = "height"
_CONF_DISPLAY_FULLSCREEN = "fullscreen"
_CONF_DISPLAY_FPS = "fps"
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
        screen_x = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH)
        screen_y = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT)
        fps = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_FPS)
        fullscreen = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN)
    except configparser.NoSectionError:
        write_settings(True)

    # controls
    # TODO

    # Audio
    # TODO


def write_settings(default=False):
    global screen_x, screen_y, fps, fullscreen
    config = configparser.RawConfigParser()

    if default:
        screen_x = 800
        screen_y = 600
        fps = 25
        fullscreen = True

    """info part"""
    config.add_section(_CONF_INFO)
    config.set(_CONF_INFO, _CONF_INFO_NAME, NAME)
    """write display configuration"""
    config.add_section(_CONF_DISPLAY)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH, screen_x)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT, screen_y)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FPS, fps)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN, fullscreen)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def init_screen():
    read_settings()
    pygame.display.set_caption(NAME)
    update_screen()


def update_screen():
    """switch to fullscreen mode"""
    global screen, screen_x, screen_y, fullscreen
    screen_resolution = pygame.display.Info()
    s_width, s_height = screen_resolution.current_w, screen_resolution.current_h

    if fullscreen:
        screen_x, screen_y = s_width, s_height
        screen = pygame.display.set_mode((screen_x, screen_y), FULLSCREEN | HWSURFACE | DOUBLEBUF, 24)
    else:
        screen = pygame.display.set_mode((screen_x, screen_y), RESIZABLE, 24)


def refresh_screen(rects=None):
    """refresh the pygame screen/window"""
    try:
        if not rects:
            screen.fill(BACKGROUND)
        pygame.display.update(rects)
    except pygame.error:
        # OpenGL can only redraw the whole screen
        pygame.display.flip()


def set_resolution(width, height):
    global screen_x, screen_y

    if width < SCREEN_MIN_X:
        screen_x = SCREEN_MIN_X
    else:
        screen_x = width
    if height < SCREEN_MIN_Y:
        screen_y = SCREEN_MIN_Y
    else:
        screen_y = height

    # update the screen
    update_screen()


def get_screen():
    return screen


def get_fps():
    return fps


def set_fps(new_fps):
    global fps
    if 0 < new_fps <= 60:
        fps = new_fps


def get_is_running():
    return game_is_running


def set_is_running(bool_run):
    global game_is_running
    game_is_running = bool_run
