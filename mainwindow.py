import pygame
import sys
import os
from pygame.locals import *
from sys import exit
import configparser
from mainmenu import Menu, MenuItem
from renderthread import RenderThread

'''constants'''
NAME = "pyRunner"
CONFIG = "config.cfg"
# Colors
BLUE = pygame.Color(30, 144, 255)
YELLOW = pygame.Color(255, 255, 0)
RED = pygame.Color(255, 0, 0)
BLACK = pygame.Color(0, 0, 0)
BACKGROUND = pygame.Color(200, 200, 200)
GRAY = pygame.Color(100, 100, 100)
WHITE = (255, 255, 255)
# Settings
_CONF_INFO = "Info"
_CONF_INFO_NAME = "name"
_CONF_DISPLAY = "Display"
_CONF_DISPLAY_WIDTH = "width"
_CONF_DISPLAY_HEIGHT = "height"
_CONF_DISPLAY_FULLSCREEN = "fullscreen"
_CONF_DISPLAY_SWITCH_RES = "switch resolution"
_CONF_DISPLAY_FPS = "fps"
'''global variables'''
game_is_running = True
screen_x = screen_y = fps = fullscreen = switch_resolution = in_menu = bg_image = None
current_menu = None
menu_pos = 1
render_thread = None


def read_settings():
    """read the settings from config.cfg"""
    global screen_x, screen_y, fps, fullscreen, switch_resolution
    try:
        config = configparser.RawConfigParser()
        config.read(CONFIG)

        '''get display configuration'''
        screen_x = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH)
        screen_y = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT)
        fps = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_FPS)
        fullscreen = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN)
        switch_resolution = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_SWITCH_RES)
    except configparser.NoSectionError:
        write_settings(True)
    except configparser.NoOptionError:
        write_settings(True)

    # controls
    # TODO

    # Audio
    # TODO


def write_settings(default=False):
    """save the current used settings

    Args:
        default (bool): true to save default values to the disk
    """
    global screen_x, screen_y, fps, fullscreen, switch_resolution
    config = configparser.RawConfigParser()

    if default:
        # default display values
        screen_x = 800
        screen_y = 600
        fps = 25
        fullscreen = True
        switch_resolution = False

    '''info part'''
    config.add_section(_CONF_INFO)
    config.set(_CONF_INFO, _CONF_INFO_NAME, NAME)
    '''write display configuration'''
    config.add_section(_CONF_DISPLAY)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH, screen_x)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT, screen_y)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FPS, fps)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN, fullscreen)
    config.set(_CONF_DISPLAY, _CONF_DISPLAY_SWITCH_RES, switch_resolution)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def init_screen():
    """initialize the main screen"""
    global render_thread
    read_settings()
    render_thread = RenderThread(NAME, screen_x, screen_y, fps, fullscreen, switch_resolution)
    render_thread.fill_screen(BACKGROUND)
    render_thread.start()


def init_menu():
    """initialize the whole main menu structure

    Cave: menus need to be saved in the reverse order (bottom to top) so that
          the top menus contain all up to date sub-menu objects
    """
    s_width = int(render_thread.screen.get_width() / 4) * 3
    s_height = int(render_thread.screen.get_height() / 3) * 2
    surface = pygame.Surface((s_width, s_height), SRCALPHA)
    # regular font sizes
    h1_size = 72
    h2_size = 48
    item_size = 36
    '''first create the root menu'''
    menu_main = Menu(surface)
    '''then calculate the ratio to adjust font sizes accordingly'''
    ratio = menu_main.calc_font_size(h1_size, item_size)
    h1_size = int(h1_size * ratio)
    h2_size = int(h2_size * ratio)
    item_size = int(item_size * ratio)
    '''then begin adding items and pass them the font sizes'''
    menu_main.add_menu_item(MenuItem(NAME, None, h1_size))
    # new game menu
    menu_new_game = Menu(surface, menu_main, item_size)
    menu_new_game.add_menu_item(MenuItem("Start Game", None, h2_size))
    menu_new_game.add_menu_item(MenuItem("Singleplayer", None, item_size))
    menu_new_game.add_menu_item(MenuItem("Multiplayer", None, item_size))
    #   single player
    menu_ng_singleplayer = Menu(surface, menu_new_game, item_size)
    menu_ng_singleplayer.add_menu_item(MenuItem("Singleplayer", None, h2_size))
    menu_ng_singleplayer.add_menu_item(MenuItem("New Game", None, item_size))
    menu_ng_singleplayer.add_menu_item(MenuItem("Resume", None, item_size))
    menu_ng_singleplayer.add_menu_item(MenuItem("Difficulty", None, item_size))
    #   multiplayer
    menu_ng_multiplayer = Menu(surface, menu_new_game, item_size)
    menu_ng_multiplayer.add_menu_item(MenuItem("Multiplayer", None, h2_size))
    menu_ng_multiplayer.add_menu_item(MenuItem("Local Game", None, item_size))
    menu_ng_multiplayer.add_menu_item(MenuItem("Network Game", None, item_size))
    menu_ng_multiplayer.add_menu_item(MenuItem("Game Settings", None, item_size))
    # settings menu
    menu_settings = Menu(surface, menu_main, item_size)
    menu_settings.add_menu_item(MenuItem("Settings", None, h2_size))
    #   video settings
    menu_s_video = Menu(surface, menu_settings, item_size)
    menu_s_video.add_menu_item(MenuItem("Video Settings", None, h2_size))
    menu_s_video_fullscreen = "Fullscreen <" + bool_to_string(fullscreen) + ">"
    menu_s_video.add_menu_item(MenuItem(menu_s_video_fullscreen, 'switch_fullscreen()', item_size))
    menu_s_video_switch_res = "Switch Resolution <" + bool_to_string(switch_resolution) + ">"
    menu_s_video.add_menu_item(MenuItem(menu_s_video_switch_res, 'switch_fs_resolution()', item_size))
    # resolutions
    if fullscreen:
        menu_s_v_resolution = Menu(surface, menu_s_video, item_size)
        menu_s_v_resolution.add_menu_item(MenuItem("Video Resolution", None, h2_size))
        for res in render_thread.display_modes:
            width, height = res
            res_name = str(width) + "x" + str(height)
            func_name = "set_resolution(" + str(width) + ", " + str(height) + ", True)"
            menu_s_v_resolution.add_menu_item(MenuItem(res_name, func_name, item_size))
        res_name = "<" + str(screen_x) + "x" + str(screen_y) + ">"
        menu_s_video.add_menu_item(MenuItem("Resolution " + res_name, menu_s_v_resolution, item_size))
    menu_s_video_showfps = "Show FPS <" + bool_to_string(render_thread.show_framerate) + ">"
    menu_s_video.add_menu_item(MenuItem(menu_s_video_showfps, 'switch_showfps()', item_size))
    '''complete the settings menu at the end to store the up to date objects'''
    menu_settings.add_menu_item(MenuItem("Audio", None, item_size))
    menu_settings.add_menu_item(MenuItem("Controls", None, item_size))
    menu_settings.add_menu_item(MenuItem("Video", menu_s_video, item_size))
    '''complete main menu at the end to store the up to date objects'''
    menu_main.add_menu_item(MenuItem("Start Game", menu_new_game, item_size))
    menu_main.add_menu_item(MenuItem("Settings", menu_settings, item_size))
    menu_main.add_menu_item(MenuItem("Exit", 'quit_game()', item_size))

    '''save the main menu'''
    set_current_menu(menu_main)


def set_current_menu(menu):
    """switch menu level

    Args:
        menu (Menu): the (sub)menu to switch to
    """
    global current_menu, menu_pos
    current_menu = menu
    menu_pos = 1
    show_menu()


def show_menu(boolean=True):
    """print the current menu to the screen"""
    global current_menu, in_menu, menu_pos, bg_image
    render_thread.fill_screen(BACKGROUND)
    # TODO add game surface here
    # surface = pygame.Surface((screen_x, screen_y))
    if bg_image.get_width() is not screen_x or bg_image.get_height() is not screen_y:
        bg_image = pygame.transform.scale(bg_image, (screen_x, screen_y))
    surface = bg_image
    # save this as background surface for dirty rects
    render_thread.bg_surface = bg_image
    render_thread.blit(surface, None, True)

    if boolean:
        in_menu = True
        current_menu.print_menu(menu_pos, menu_pos, True)
        render_thread.blit(current_menu.surface, None, True)
    else:
        in_menu = False
        menu_pos = 1
    # draw the selected surface to the screen
    render_thread.refresh_screen(True)


def navigate_menu(old_pos, complete=False):
    """helps rerendering the changed menu items for partial screen updates"""
    rects = current_menu.print_menu(menu_pos, old_pos, complete)
    render_thread.blit(current_menu.surface, None, True)
    render_thread.add_rect_to_update(rects)


def do_menu_action():
    """try to evaluate if a menu action is either a sub-menu or a function to call"""
    try:
        action = current_menu.get_menu_item(menu_pos).action
        if type(action) is Menu:
            set_current_menu(action)
        else:
            eval(action)()
    except TypeError:
        # don't crash on wrong actions, the menu will stay up and nothing will happen
        pass


def bool_to_string(boolean):
    """helper function for the MenuItems containing booleans in their name"""
    if boolean:
        return "on"
    else:
        return "off"


def set_resolution(width, height, restart=False):
    """set the main screen/surface resolution

    Args:
        width (int): new width
        height (int): new height
        restart (bool): restart this process for a clean initialization
    """
    global screen_x, screen_y
    screen_x = width
    screen_y = height

    if restart:
        '''save changed settings to disk and restart this program'''
        write_settings()
        restart_program()
    else:
        render_thread.set_resolution(screen_x, screen_y)


def switch_fullscreen():
    """switch between windowed and fullscreen mode"""
    global fullscreen
    fullscreen = False if fullscreen else True
    '''save changed settings to disk and restart this program'''
    write_settings()
    restart_program()


def switch_showfps():
    """switch fps overlay on/off"""
    new = False if render_thread.show_framerate else True
    render_thread.show_framerate = new
    item = current_menu.get_menu_item(menu_pos)
    if item.action == 'switch_showfps()':
        item.text = "Show FPS <" + bool_to_string(new) + ">"
        show_menu(True)


def switch_fs_resolution():
    """switch between windowed and fullscreen mode"""
    global switch_resolution
    switch_resolution = False if switch_resolution else True
    '''save changed settings to disk and restart this program'''
    # workaround: else pygame is getting the wrong screen dimensions
    render_thread.fullscreen = False
    write_settings()
    restart_program()


def quit_game():
    """quit the game"""
    render_thread.stop_thread()
    pygame.quit()
    exit()


def restart_program():
    """Restarts the current program"""
    python = sys.executable
    os.execl(python, python, * sys.argv)


def init_game():
    global bg_image
    """initialize the game variables"""
    # initialize the main screen
    init_screen()
    # load images
    bg_image = pygame.image.load(os.path.join('./resources/images/', 'lode2.gif')).convert()
    # initialize the main menu
    init_menu()


def start_game():
    """start the game"""
    global screen_x, screen_y, fps, menu_pos
    # PyGame initialization
    init_game()
    # Main loop relevant vars
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                quit_game()
            elif event.type == VIDEORESIZE:
                '''notice window size changes in windowed mode'''
                x, y = event.dict['size']
                render_thread.set_resolution(x, y)
                init_menu()
            elif event.type == KEYDOWN:
                '''key pressing events'''
                if game_is_running:
                    if event.key == K_LEFT:
                        pass
                    if event.key == K_RIGHT:
                        pass
                    if event.key == K_UP:
                        if in_menu:
                            if 1 < menu_pos:
                                menu_pos -= 1
                                navigate_menu(menu_pos + 1)
                    if event.key == K_DOWN:
                        if in_menu:
                            if menu_pos < current_menu.length - 1:
                                menu_pos += 1
                                navigate_menu(menu_pos - 1)
                    if event.key == K_RETURN:
                        if in_menu:
                            do_menu_action()
                    if event.key == K_ESCAPE:
                        if in_menu:
                            back_item = current_menu.get_menu_item(current_menu.length - 1).action
                            if type(back_item) is Menu:
                                set_current_menu(back_item)
                            else:
                                show_menu(False)
                        else:
                            show_menu()
                else:
                    if event.key == K_ESCAPE:
                        quit_game()

        # save cpu resources
        clock.tick(fps)


# start the 4 in a row game
start_game()
