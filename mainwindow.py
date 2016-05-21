#!/usr/bin/python
# -*- coding: utf-8 -*-
import pygame
from pygame.locals import *
import sys
import os
from sys import exit
try:
    # Python 3
    import configparser
except ImportError:
    # Python 2
    import ConfigParser
from mainmenu import Menu, MenuItem
from renderthread import RenderThread
from musicthread import MusicMixer

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
_CONF_AUDIO = "Audio"
_CONF_AUDIO_VOL = " volume"
_CONF_AUDIO_MUSIC = "music"
_CONF_AUDIO_MUSIC_VOL = _CONF_AUDIO_MUSIC + _CONF_AUDIO_VOL
_CONF_AUDIO_SFX = "sfx"
_CONF_AUDIO_SFX_VOL = _CONF_AUDIO_SFX + _CONF_AUDIO_VOL
'''global variables'''
game_is_running = True
screen_x = screen_y = fps = fullscreen = switch_resolution = in_menu = bg_image = None
play_music = vol_music = play_sfx = vol_sfx = None
current_menu = None
menu_pos = 1
render_thread = None
music_thread = None


def get_config_parser():
    """get the adequate config parser for either python 2 or 3

    Returns: ConfigParser (Python 2) or configparser (Python 3)
    """
    try:
        config = configparser.RawConfigParser()
    except NameError:
        config = ConfigParser.RawConfigParser()
    return config


def read_settings():
    """read the settings from config.cfg"""
    global screen_x, screen_y, fps, fullscreen, switch_resolution
    global play_music, vol_music, play_sfx, vol_sfx
    try:
        config = get_config_parser()
        config.read(CONFIG)

        '''get display configuration'''
        screen_x = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH)
        screen_y = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT)
        fps = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_FPS)
        fullscreen = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN)
        switch_resolution = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_SWITCH_RES)
        play_music = config.getboolean(_CONF_AUDIO, _CONF_AUDIO_MUSIC)
        vol_music = config.getint(_CONF_AUDIO, _CONF_AUDIO_MUSIC_VOL)
        play_sfx = config.getboolean(_CONF_AUDIO, _CONF_AUDIO_SFX)
        vol_sfx = config.getint(_CONF_AUDIO, _CONF_AUDIO_SFX_VOL)
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
    global play_music, vol_music, play_sfx, vol_sfx
    config = get_config_parser()

    if default:
        # default display values
        screen_x = 800
        screen_y = 600
        fps = 25
        fullscreen = True
        switch_resolution = False
        # default audio settings
        play_music = True
        vol_music = 10
        play_sfx = True
        vol_sfx = 10

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
    '''and audio settings'''
    config.add_section(_CONF_AUDIO)
    config.set(_CONF_AUDIO, _CONF_AUDIO_MUSIC, play_music)
    config.set(_CONF_AUDIO, _CONF_AUDIO_MUSIC_VOL, vol_music)
    config.set(_CONF_AUDIO, _CONF_AUDIO_SFX, play_sfx)
    config.set(_CONF_AUDIO, _CONF_AUDIO_SFX_VOL, vol_sfx)

    with open(CONFIG, 'w') as configfile:
        config.write(configfile)


def init_audio():
    global music_thread
    music_thread = MusicMixer(play_music, vol_music, play_sfx, vol_sfx, fps)
    music_thread.background_music = ('time_delay.wav', 1)
    music_thread.start()


def init_screen():
    """initialize the main screen"""
    global render_thread
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
    screen = render_thread
    # regular font sizes
    h1_size = 72
    h2_size = 48
    item_size = 36
    '''first create the root menu'''
    menu_main = Menu(surface, screen)
    '''then calculate the ratio to adjust font sizes accordingly'''
    ratio = menu_main.calc_font_size(h1_size, item_size)
    h1_size = int(h1_size * ratio)
    h2_size = int(h2_size * ratio)
    item_size = int(item_size * ratio)
    '''then begin adding items and pass them the font sizes'''
    menu_main.add_menu_item(MenuItem(NAME, None, h1_size))
    # new game menu
    menu_new_game = Menu(surface, screen, menu_main, item_size)
    menu_new_game.add_menu_item(MenuItem("Start Game", None, h2_size))
    menu_new_game.add_menu_item(MenuItem("Singleplayer", None, item_size))
    menu_new_game.add_menu_item(MenuItem("Multiplayer", None, item_size))
    #   single player
    menu_ng_singleplayer = Menu(surface, screen, menu_new_game, item_size)
    menu_ng_singleplayer.add_menu_item(MenuItem("Singleplayer", None, h2_size))
    menu_ng_singleplayer.add_menu_item(MenuItem("New Game", None, item_size))
    menu_ng_singleplayer.add_menu_item(MenuItem("Resume", None, item_size))
    menu_ng_singleplayer.add_menu_item(MenuItem("Difficulty", None, item_size))
    #   multiplayer
    menu_ng_multiplayer = Menu(surface, screen, menu_new_game, item_size)
    menu_ng_multiplayer.add_menu_item(MenuItem("Multiplayer", None, h2_size))
    menu_ng_multiplayer.add_menu_item(MenuItem("Local Game", None, item_size))
    menu_ng_multiplayer.add_menu_item(MenuItem("Network Game", None, item_size))
    menu_ng_multiplayer.add_menu_item(MenuItem("Game Settings", None, item_size))
    # settings menu
    menu_settings = Menu(surface, screen, menu_main, item_size)
    menu_settings.add_menu_item(MenuItem("Settings", None, h2_size))
    menu_s_audio = Menu(surface, screen, menu_settings, item_size)
    menu_s_audio.add_menu_item(MenuItem("Audio Settings", None, h2_size))
    menu_s_audio_music = get_button_text("Music", music_thread.play_music)
    menu_s_audio.add_menu_item(MenuItem(menu_s_audio_music, 'switch_audio_volume(1, 0)', item_size))
    menu_s_audio_sfx = get_button_text("Sounds", music_thread.play_sfx)
    menu_s_audio.add_menu_item(MenuItem(menu_s_audio_sfx, 'switch_audio_volume(2, 0)', item_size))
    #   video settings
    menu_s_video = Menu(surface, screen, menu_settings, item_size)
    menu_s_video.add_menu_item(MenuItem("Video Settings", None, h2_size))
    menu_s_video.add_menu_item(MenuItem(get_button_text("Fullscreen", fullscreen), 'switch_fullscreen()', item_size))
    menu_s_video_switch_res = get_button_text("Switch Resolution", switch_resolution)
    menu_s_video.add_menu_item(MenuItem(menu_s_video_switch_res, 'switch_fs_resolution()', item_size))
    # resolutions
    if fullscreen:
        menu_s_v_resolution = Menu(surface, screen, menu_s_video, item_size)
        menu_s_v_resolution.add_menu_item(MenuItem("Video Resolution", None, h2_size))
        for res in render_thread.display_modes:
            width, height = res
            res_name = str(width) + "x" + str(height)
            func_name = "set_resolution(" + str(width) + ", " + str(height) + ", True)"
            menu_s_v_resolution.add_menu_item(MenuItem(res_name, func_name, item_size))
        res_name = str(screen_x) + "x" + str(screen_y)
        menu_s_video.add_menu_item(MenuItem(get_button_text("Resolution", res_name), menu_s_v_resolution, item_size))
    menu_s_video_showfps = get_button_text("Show FPS", render_thread.show_framerate)
    menu_s_video.add_menu_item(MenuItem(menu_s_video_showfps, 'switch_showfps()', item_size))
    '''complete the settings menu at the end to store the up to date objects'''
    menu_settings.add_menu_item(MenuItem("Audio", menu_s_audio, item_size))
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
        rects = current_menu.print_menu(menu_pos, menu_pos, True)
        render_thread.blit(current_menu.surface, None, True)
        render_thread.add_rect_to_update(rects)
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
            try:
                eval(action)()
            except NameError:
                print(action + " is no valid function")
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
        item.text = get_button_text("Show FPS", new)
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


def get_button_text(text, text_val):
    """ this function beautifies menu entries which contain additional information in it's name

    Args:
        text (str): the base text / name of the MenuItem
        text_val (str or bool): the value to append to the base text / name

    Returns: a formatted string to use as the MenuItem text
    """

    def print_audio_volume_bar(vol):
        """ a little helper function to visualize the volume level of a specific channel
        Args:
            vol (int): value from 0 to 10 which get's filled according to the volume level

        Returns: a 10 character long string representing the volume bar
        """
        ret_str = ""
        for i in range(10):
            if i < vol:
                ret_str += "»"
            else:
                ret_str += " "
        return ret_str

    info_str = False

    if type(text_val) is bool:
        text_val = bool_to_string(text_val)
        if text is "Music":
            info_str = print_audio_volume_bar(music_thread.music_volume)
        elif text is "Sounds":
            info_str = print_audio_volume_bar(music_thread.sfx_volume)
    elif type(text_val) is str:
        if text is "Resolution":
            return '{:<24s} {:>10s}'.format(text, text_val)

    if info_str:
        return '{:<10s} {:<4s} {:12s}'.format(text, text_val, info_str)
    else:
        return '{:<28s} {:>6s}'.format(text, text_val)


def switch_audio_volume(num, change):
    """Function to switch the Music and Sound FX volume with the left/right keys
       when hovering the Music or Sound FX on/off Menu Item

    Args:
        num (int): number of the audio channel (1) Music (2) Sound FX
        change (int): value how to change the current volume
                        -1 decrease volume by 10%
                         0 turn channel on/off
                        +1 increase volume by 10%

        additionally this function will turn the channel off if it's volume is 0
        and turn it back on when the volume get's increased starting at 0
    """
    '''wrappers for thread variables which keep a local copy of the settings so they can be saved on exit'''
    def set_music(m_bol):
        global play_music
        play_music = music_thread.play_music = m_bol
        return m_bol

    def set_music_vol(m_vol):
        global vol_music
        vol_music = music_thread.music_volume = m_vol

    def set_sfx(s_bol):
        global play_sfx
        play_sfx = music_thread.play_sfx = s_bol
        return s_bol

    def set_sfx_vol(s_vol):
        global vol_sfx
        vol_sfx = music_thread.sfx_volume = s_vol

    # to store the settings so they can be saved on exit
    item = current_menu.get_menu_item(menu_pos)
    txt = bol = vol = None
    if num is 1:
        vol = music_thread.music_volume
    elif num is 2:
        vol = music_thread.sfx_volume

    if 0 <= vol + change <= 10:
        '''in/decrease the volume'''
        old_vol = vol
        vol += change
        if num is 1:
            txt = "Music"
            bol = music_thread.play_music
            '''switch music on or off if 0 is passed'''
            if change is not 0:
                set_music_vol(vol)
                if vol is 0:
                    bol = set_music(False)
                if old_vol is 0:
                    bol = set_music(True)
            else:
                bol = False if bol else True
                set_music(bol)
                if vol is 0:
                    set_music_vol(1)
        elif num is 2:
            txt = "Sounds"
            bol = music_thread.play_sfx
            '''switch sfx on or off if 0 is passed'''
            if change is not 0:
                set_sfx_vol(vol)
                if vol is 0:
                    bol = set_sfx(False)
                if old_vol is 0:
                    bol = set_sfx(True)
            else:
                bol = False if bol else True
                set_sfx(bol)
                if vol is 0:
                    set_sfx_vol(1)
        '''update the menu button'''
        item.text = get_button_text(txt, bol)
        '''and refresh the menu'''
        show_menu(True)


def quit_game():
    """quit the game"""
    write_settings()
    render_thread.stop_thread()
    music_thread.stop_thread()
    pygame.quit()
    exit()


def restart_program():
    """Restarts the current program"""
    python = sys.executable
    os.execl(python, python, * sys.argv)


def init_game():
    global bg_image
    """initialize the game variables"""
    # first read the settings
    read_settings()
    # init audio subsystem first to avoid lag
    init_audio()
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

    # switch music (test)
    music_thread.background_music = ('summers_end_acoustic.aif', 0)

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
                    if event.key == K_SPACE:
                        music_thread.play_sound('9_mm_gunshot-mike-koenig-123.wav')
                    if event.key == K_LSHIFT:
                        music_thread.play_sound('unscrew_lightbulb-mike-koenig.wav')
                    if event.key == K_LEFT:
                        if in_menu:
                            action = current_menu.get_menu_item(menu_pos).action
                            if action == 'switch_audio_volume(1, 0)':
                                switch_audio_volume(1, -1)
                            elif action == 'switch_audio_volume(2, 0)':
                                switch_audio_volume(2, -1)
                    if event.key == K_RIGHT:
                        if in_menu:
                            action = current_menu.get_menu_item(menu_pos).action
                            if action == 'switch_audio_volume(1, 0)':
                                switch_audio_volume(1, 1)
                            elif action == 'switch_audio_volume(2, 0)':
                                switch_audio_volume(2, 1)
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
