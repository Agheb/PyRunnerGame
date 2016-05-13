import pygame
from pygame.locals import *
from sys import exit
import configparser
from mainmenu import Menu, MenuItem

"""constants"""
NAME = "pyRunner"
CONFIG = "config.cfg"
MENU_FONT = "./resources/fonts/Angeline_Vintage_Demo.otf"
# Minimum Fullscreen Resolution
SCREEN_MIN_X = 640
SCREEN_MIN_Y = 480
# Minimum Windowed Resolution
WINDOW_MIN_X = SCREEN_MIN_X - 40
WINDOW_MIN_Y = SCREEN_MIN_Y - 80
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
game_is_running = None
screen = screen_x = screen_y = fps = fullscreen = upscale = menu_options = None


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
    read_settings()
    pygame.display.set_caption(NAME)
    update_screen()
    screen.fill(BACKGROUND)


def update_screen():
    """switch to fullscreen mode"""
    global screen, screen_x, screen_y, fullscreen, upscale

    if fullscreen:
        if not upscale:
            screen_resolution = pygame.display.Info()
            s_width, s_height = screen_resolution.current_w, screen_resolution.current_h
            screen_x, screen_y = s_width, s_height
        screen = pygame.display.set_mode((screen_x, screen_y), FULLSCREEN | HWSURFACE | DOUBLEBUF, 24)
    else:
        screen = pygame.display.set_mode((screen_x, screen_y), RESIZABLE, 24)


def refresh_screen(rects=None):
    """refresh the pygame screen/window"""
    try:
        # screen.fill(BACKGROUND)

        if not rects:
            pygame.display.update()
        else:
            pygame.display.update(rects)
    except pygame.error:
        # OpenGL can only redraw the whole screen
        pygame.display.flip()


def set_resolution(width, height):
    global screen_x, screen_y

    if fullscreen:
        screen_x = SCREEN_MIN_X if width < SCREEN_MIN_X else width
        screen_y = SCREEN_MIN_Y if height < SCREEN_MIN_Y else height
    else:
        screen_x = WINDOW_MIN_X if width < WINDOW_MIN_X else width
        screen_y = WINDOW_MIN_Y if height < WINDOW_MIN_Y else height

    # update the screen
    update_screen()


def get_screen():
    return screen


def init_menu():
    global menu_options
    pygame.font.init()
    menu = Menu(screen)
    menu_options = [MenuItem(NAME, 30, 72), MenuItem("New Game", 150), MenuItem("Multiplayer", 225),
                    MenuItem("Settings", 300), MenuItem("Exit", 375)]

def print_menu(options):
    # while True:
        # pygame.event.pump()

    for x in range(0, len(options)):
        option = options[x]
        pygame.draw.rect(screen, BACKGROUND, option.rect)

        if x is 0:
            option.hovered = True
        else:
            if option.rect.collidepoint(pygame.mouse.get_pos()):
                option.hovered = True
            else:
                option.hovered = False
        option.draw()

        refresh_screen(option.rect)

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
    global screen_x, screen_y, screen, fps
    # PyGame initialization
    pygame.init()
    init_game()
    clock = pygame.time.Clock()
    refresh_counter = 0

    # init screen
    refresh_screen()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            elif event.type == VIDEORESIZE:
                x, y = event.dict['size']
                set_resolution(x, y)
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
                        init_game()
                    if event.key == K_r:
                        init_game()
            # in case the game board disappears after switching to full screen on macos x
            elif event.type == MOUSEBUTTONDOWN:
                if game_is_running:
                    refresh_screen()
                # x, y = pygame.mouse.get_pos()
            elif event.type == MOUSEMOTION:
                print_menu(menu_options)

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
