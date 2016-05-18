import pygame
from pygame.locals import *
from sys import exit
import configparser
from mainmenu import Menu, MenuItem
from renderthread import RenderThread

"""constants"""
NAME = "pyRunner"
CONFIG = "config.cfg"
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
screen_x = screen_y = fps = fullscreen = upscale = None
current_menu = None
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
    surface = render_thread.get_screen()
    # main menu
    menu_main = Menu(surface)
    menu_main.add_menu_item(MenuItem(NAME, None, 72))
    # new game menu
    menu_new_game = Menu(surface, menu_main)
    menu_new_game.add_menu_item(MenuItem("Start Game", None, 72))
    menu_new_game.add_menu_item(MenuItem("Singleplayer", None))
    menu_new_game.add_menu_item(MenuItem("Multiplayer", None))
    #   single player
    menu_ng_singleplayer = Menu(surface, menu_new_game)
    menu_ng_singleplayer.add_menu_item(MenuItem("Singleplayer", None, 72))
    menu_ng_singleplayer.add_menu_item(MenuItem("New Game", None))
    menu_ng_singleplayer.add_menu_item(MenuItem("Resume", None))
    menu_ng_singleplayer.add_menu_item(MenuItem("Difficulty", None))
    #   multiplayer
    menu_ng_multiplayer = Menu(surface, menu_new_game)
    menu_ng_multiplayer.add_menu_item(MenuItem("Multiplayer", None, 72))
    menu_ng_multiplayer.add_menu_item(MenuItem("Local Game", None))
    menu_ng_multiplayer.add_menu_item(MenuItem("Network Game", None))
    menu_ng_multiplayer.add_menu_item(MenuItem("Game Settings", None))
    # settings menu
    menu_settings = Menu(surface, menu_main)
    menu_settings.add_menu_item(MenuItem("Settings", None, 72))
    #   video settings
    menu_s_video = Menu(surface, menu_settings)
    menu_s_video.add_menu_item(MenuItem("Video Settings", None, 72))
    menu_s_video.add_menu_item(MenuItem("Fullscreen " + bool_to_string(fullscreen), None))
    # complete the settings menu at the end to store the up to date objects
    menu_settings.add_menu_item(MenuItem("Audio", None))
    menu_settings.add_menu_item(MenuItem("Controls", None))
    menu_settings.add_menu_item(MenuItem("Video", menu_s_video))
    # complete main menu at the end to store the up to date objects
    menu_main.add_menu_item(MenuItem("Start Game", menu_new_game))
    menu_main.add_menu_item(MenuItem("Settings", menu_settings))
    menu_main.add_menu_item(MenuItem("Exit", 'quit_game()'))

    switch_menu(menu_main)


def switch_menu(menu):
    global current_menu
    current_menu = menu
    show_menu()


def show_menu():
    global current_menu, menu_pos
    render_thread.fill_screen(BACKGROUND)
    menu_pos = 1
    current_menu.print_menu(menu_pos, 0)
    render_thread.refresh_screen(True)


def bool_to_string(blean):
    if blean:
        return "on"
    else:
        return "off"


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


def start_game():
    """start the game"""
    global screen_x, screen_y, fps, menu_pos
    # PyGame initialization
    init_game()
    clock = pygame.time.Clock()

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
                            render_thread.add_rect_to_update(current_menu.print_menu(menu_pos, menu_pos + 1, False))
                    if event.key == K_DOWN:
                        if menu_pos < current_menu.get_length() - 1:
                            menu_pos += 1
                            render_thread.add_rect_to_update(current_menu.print_menu(menu_pos, menu_pos - 1, False))
                    if event.key == K_RETURN:
                        try:
                            action = current_menu.get_menu_item(menu_pos).get_action()
                            if type(action) is Menu:
                                switch_menu(action)
                            else:
                                eval(action)()
                        except TypeError:
                            pass
                else:
                    if event.key == K_n:
                        init_game()
                    if event.key == K_r:
                        init_game()

        # save cpu resources
        clock.tick(fps)


# start the 4 in a row game
start_game()
