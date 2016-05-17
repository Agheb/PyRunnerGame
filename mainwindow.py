import pygame
from pygame.locals import *
from sys import exit
import configparser
from mainmenu import Menu, MenuItem, print_menu
from renderthread import RenderThread

"""constants"""
NAME = "pyRunner"
CONFIG = "config.cfg"
MENU_FONT = "./resources/fonts/Angeline_Vintage_Demo.otf"
# Colors
BLUE = pygame.Color(30, 144, 255)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)
BLACK = pygame.Color(0, 0, 0)
BACKGROUND = pygame.Color(200, 200, 200)
GRAY = pygame.Color(100, 100, 100)
# Settings
_CONF_INFO = "Info"
_CONF_INFO_NAME = "name"
_CONF_DISPLAY = "Display"
_CONF_DISPLAY_WIDTH = "width"
_CONF_DISPLAY_HEIGHT = "height"
_CONF_DISPLAY_FULLSCREEN = "fullscreen"
_CONF_DISPLAY_UPSCALE = "upscale"
_CONF_DISPLAY_FPS = "fps"
"""global variables"""
game_is_running = True
screen_x = screen_y = fps = fullscreen = upscale = menu = menu_options = None
menu_pos = 1
render_thread = None


def read_settings():
    """read the settings from config.cfg"""
    global screen_x, screen_y, fps, fullscreen, upscale
    try:
        config = configparser.RawConfigParser()
        config.read(CONFIG)

        """get display configuration"""
        screen_x = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH)
        screen_y = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT)
        fps = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_FPS)
        fullscreen = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN)
        upscale = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_UPSCALE)
    except configparser.NoSectionError:
        write_settings(True)
    except configparser.NoOptionError:
        write_settings(True)

    # controls
    # TODO

    # Audio
    # TODO


def write_settings(default=False):
    global screen_x, screen_y, fps, fullscreen, upscale
    config = configparser.RawConfigParser()

    if default:
        # default display values
        screen_x = 800
        screen_y = 600
        fps = 25
        fullscreen = True
        upscale = False

    """info part"""
    config.add_section(_CONF_INFO)
    config.set(_CONF_INFO, _CONF_INFO_NAME, NAME)
    """write display configuration"""
    config.add_section(_CONF_DISPLAY)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH, screen_x)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT, screen_y)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FPS, fps)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN, fullscreen)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_UPSCALE, upscale)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def init_screen():
    global render_thread
    read_settings()
    render_thread = RenderThread(NAME, screen_x, screen_y, fps, fullscreen, upscale)
    render_thread.fill_screen(BACKGROUND)
    render_thread.start()


def init_menu():
    menu = Menu(render_thread.get_screen())
    switch_menu("main")


def switch_menu(menuname):
    global menu_options, menu_pos
    render_thread.fill_screen(BACKGROUND)
    menu_pos = 1
    if menuname == "new":
        menu_options = [MenuItem("New Game", None, 30, 48), MenuItem("Single Player", None, 150),
                     MenuItem("Multiplayer", None, 225),
                     MenuItem("Back", 'switch_menu("main")', 300)]
    elif menuname == "main":
        menu_options = [MenuItem(NAME, None, 30, 72), MenuItem("New Game", 'switch_menu("new")', 150),
                        MenuItem("Multiplayer", None, 225),
                        MenuItem("Settings", None, 300), MenuItem("Exit", 'quit_game()', 375)]

    print_menu(menu_options)
    render_thread.refresh_screen(True)


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


def quit_game():
    """quit the game"""
    render_thread.stop_thread()
    pygame.quit()
    exit()


def init_game():
    """initialize the game variables"""
    # initialize main screen
    init_screen()
    init_menu()
    print_menu(menu_options)

def start_game():
    """start the game"""
    global screen_x, screen_y, fps, menu_pos
    # PyGame initialization
    init_game()
    clock = pygame.time.Clock()

    try:
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    quit_game()
                elif event.type == VIDEORESIZE:
                    x, y = event.dict['size']
                    render_thread.set_resolution(x, y)
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        quit_game()
                    if game_is_running:
                        if event.key == K_LEFT:
                            pass
                        if event.key == K_RIGHT:
                            pass
                        if event.key == K_UP:
                            if 1 < menu_pos:
                                menu_pos -= 1
                                render_thread.add_rect_to_update(print_menu(menu_options, menu_pos, menu_pos + 1, False))
                        if event.key == K_DOWN:
                            if menu_pos < len(menu_options) - 1:
                                menu_pos += 1
                                render_thread.add_rect_to_update(print_menu(menu_options, menu_pos, menu_pos - 1, False))
                        if event.key == K_RETURN:
                            func = eval(menu_options[menu_pos].get_action())
                            if func:
                                func()
                    else:
                        if event.key == K_n:
                            init_game()
                        if event.key == K_r:
                            init_game()

            # save cpu resources
            clock.tick(fps)
    # if the menu functions are not set yet
    except TypeError:
        # make sure the application shuts down correctly on errors
        render_thread.stop_thread()
        raise


# start the 4 in a row game
start_game()
