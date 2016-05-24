#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
try:
    import configparser     # Python 3
except ImportError:
    import ConfigParser     # Python 2
# universal imports
import pygame
from pygame.locals import *
import sys
import os
# pyRunner subclasses
from pyrunner_classes import *

'''constants'''
NAME = "pyRunner"
CONFIG = "resources/config.cfg"
# Colors
BLUE = (30, 144, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
BACKGROUND = (200, 200, 200)
GRAY = (100, 100, 100)
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


class PyRunner(object):
    """main PyRunner Class

       This class runs the whole game an initializes all necessary values
    """

    def __init__(self):
        """initialize the game"""
        self.name = "PyRunner"
        '''important settings'''
        self.game_is_running = True
        '''screen settings'''
        self.screen_x = None
        self.screen_y = None
        self.fps = None
        self.fullscreen = None
        self.switch_resolution = None
        self.in_menu = None
        self.bg_image = None
        '''audio settings'''
        self.play_music = None
        self.vol_music = None
        self.play_sfx = None
        self.vol_sfx = None
        '''controls for player 1'''
        self.p1_left = None
        self.p1_right = None
        self.p1_up = None
        self.p1_down = None
        self.p1_action_l = None
        self.p1_action_r = None
        self.p1_interact = None
        self.p1_taunt = None
        '''controls for player 2'''
        self.p2_left = None
        self.p2_right = None
        self.p2_up = None
        self.p2_down = None
        self.p2_action_l = None
        self.p2_action_r = None
        self.p2_interact = None
        self.p2_taunt = None
        # initialize the settings
        self.config_parser = self.init_config_parser()
        self.read_settings()
        '''init the audio subsystem prior to anything else'''
        self.music_thread = MusicMixer(self.play_music, self.vol_music, self.play_sfx, self.vol_sfx, self.fps)
        self.music_thread.background_music = ('time_delay.wav', 1)
        self.music_thread.start()
        '''init the main screen'''
        self.render_thread = RenderThread(NAME, self.screen_x, self.screen_y, self.fps,
                                          self.fullscreen, self.switch_resolution)
        self.render_thread.fill_screen(BACKGROUND)
        self.render_thread.start()
        # set the background image
        self.bg_image = pygame.image.load(os.path.join('./resources/images/', 'lode2.gif')).convert()
        '''init the main menu'''
        self.menu_pos = 1
        self.current_menu = None
        self.init_menu()

    @staticmethod
    def init_config_parser():
        """get the adequate config parser for either python 2 or 3

        Returns: ConfigParser (Python 2) or configparser (Python 3)
        """
        try:
            return configparser.RawConfigParser()
        except NameError:
            return ConfigParser.RawConfigParser()

    def read_settings(self):
        """read the settings from config.cfg"""
        try:
            config = self.config_parser

            config.read(CONFIG)

            '''get display configuration'''
            self.screen_x = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH)
            self.screen_y = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT)
            self.fps = config.getint(_CONF_DISPLAY, _CONF_DISPLAY_FPS)
            self.fullscreen = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN)
            self.switch_resolution = config.getboolean(_CONF_DISPLAY, _CONF_DISPLAY_SWITCH_RES)
            '''audio settings'''
            self.play_music = config.getboolean(_CONF_AUDIO, _CONF_AUDIO_MUSIC)
            self.vol_music = config.getint(_CONF_AUDIO, _CONF_AUDIO_MUSIC_VOL)
            self.play_sfx = config.getboolean(_CONF_AUDIO, _CONF_AUDIO_SFX)
            self.vol_sfx = config.getint(_CONF_AUDIO, _CONF_AUDIO_SFX_VOL)
        except configparser.NoSectionError or configparser.NoOptionError:
            self.write_settings(True)

        # controls
        # TODO

    def write_settings(self, default=False):
        """save the current used settings

        Args:
            default (bool): true to save default values to the disk
        """
        '''Python 3 vs Python 2 error handling'''
        try:
            cp_duplicate_section_error = configparser.DuplicateSectionError
        except NameError:
            cp_duplicate_section_error = ConfigParser.DuplicateSectionError
        try:
            cp_permission_error = PermissionError
        except NameError:
            cp_permission_error = (IOError, OSError)

        try:
            config = self.config_parser

            if default:
                # default display values
                self.screen_x = 800
                self.screen_y = 600
                self.fps = 25
                self.fullscreen = True
                self.switch_resolution = False
                # default audio settings
                self.play_music = True
                self.vol_music = 10
                self.play_sfx = True
                self.vol_sfx = 10

            '''info part'''
            try:
                config.add_section(_CONF_INFO)
            except cp_duplicate_section_error:
                pass
            config.set(_CONF_INFO, _CONF_INFO_NAME, NAME)
            '''write display configuration'''
            try:
                config.add_section(_CONF_DISPLAY)
            except cp_duplicate_section_error:
                pass
            config.set(_CONF_DISPLAY, _CONF_DISPLAY_WIDTH, self.screen_x)
            config.set(_CONF_DISPLAY, _CONF_DISPLAY_HEIGHT, self.screen_y)
            config.set(_CONF_DISPLAY, _CONF_DISPLAY_FPS, self.fps)
            config.set(_CONF_DISPLAY, _CONF_DISPLAY_FULLSCREEN, self.fullscreen)
            config.set(_CONF_DISPLAY, _CONF_DISPLAY_SWITCH_RES, self.switch_resolution)
            '''and audio settings'''
            try:
                config.add_section(_CONF_AUDIO)
            except cp_duplicate_section_error:
                pass
            config.set(_CONF_AUDIO, _CONF_AUDIO_MUSIC, self.play_music)
            config.set(_CONF_AUDIO, _CONF_AUDIO_MUSIC_VOL, self.vol_music)
            config.set(_CONF_AUDIO, _CONF_AUDIO_SFX, self.play_sfx)
            config.set(_CONF_AUDIO, _CONF_AUDIO_SFX_VOL, self.vol_sfx)

            with open(CONFIG, 'w') as configfile:
                config.write(configfile)
        except cp_permission_error:
            print("The config file is locked or not writable.")
            print("Please delete config.cfg or make sure you have write access")

    # noinspection PyTypeChecker
    def init_menu(self):
        """initialize the whole main menu structure

        Cave: menus need to be saved in the reverse order (bottom to top) so that
              the top menus contain all up to date sub-menu objects
        """
        s_width = (self.render_thread.screen.get_width() // 4) * 3
        s_height = (self.render_thread.screen.get_height() // 3) * 2
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
        menu_s_audio = Menu(surface, menu_settings, item_size)
        menu_s_audio.add_menu_item(MenuItem("Audio Settings", None, h2_size))
        menu_s_audio_music = self.get_button_text("Music", self.music_thread.play_music)
        menu_s_audio.add_menu_item(MenuItem(menu_s_audio_music, 'switch_audio_volume(1, 0)', item_size))
        menu_s_audio_sfx = self.get_button_text("Sounds", self.music_thread.play_sfx)
        menu_s_audio.add_menu_item(MenuItem(menu_s_audio_sfx, 'switch_audio_volume(2, 0)', item_size))
        #   video settings
        menu_s_video = Menu(surface, menu_settings, item_size)
        menu_s_video.add_menu_item(MenuItem("Video Settings", None, h2_size))
        menu_s_video.add_menu_item(MenuItem(self.get_button_text("Fullscreen", self.fullscreen),
                                            'switch_fullscreen()', item_size))
        menu_s_video_switch_res = self.get_button_text("Switch Resolution", self.switch_resolution)
        menu_s_video.add_menu_item(MenuItem(menu_s_video_switch_res, 'switch_fs_resolution()', item_size))
        # resolutions
        menu_s_v_resolution = Menu(surface, menu_s_video, item_size)
        menu_s_v_resolution.add_menu_item(MenuItem("Video Resolution", None, h2_size))
        for res in self.render_thread.display_modes:
            width, height = res
            res_name = str(width) + "x" + str(height)
            func_name = "set_resolution(" + str(width) + ", " + str(height) + ", True)"
            menu_s_v_resolution.add_menu_item(MenuItem(res_name, func_name, item_size))
        res_name = str(self.screen_x) + "x" + str(self.screen_y)
        menu_s_video.add_menu_item(MenuItem(self.get_button_text("Resolution", res_name), menu_s_v_resolution, item_size))
        menu_s_video_show_fps = self.get_button_text("Show FPS", self.render_thread.show_framerate)
        menu_s_video.add_menu_item(MenuItem(menu_s_video_show_fps, 'switch_show_fps()', item_size))
        '''complete the settings menu at the end to store the up to date objects'''
        menu_settings.add_menu_item(MenuItem("Audio", menu_s_audio, item_size))
        menu_settings.add_menu_item(MenuItem("Controls", None, item_size))
        menu_settings.add_menu_item(MenuItem("Video", menu_s_video, item_size))
        '''complete main menu at the end to store the up to date objects'''
        menu_main.add_menu_item(MenuItem("Start Game", menu_new_game, item_size))
        menu_main.add_menu_item(MenuItem("Settings", menu_settings, item_size))
        menu_main.add_menu_item(MenuItem("Exit", 'quit_game()', item_size))

        '''save the main menu'''
        self.set_current_menu(menu_main)

    def set_current_menu(self, new_menu):
        """switch menu level

        Args:
            new_menu (Menu): the (sub)menu to switch to
        """
        self.current_menu = new_menu
        self.menu_pos = 1
        self.show_menu()

    def show_menu(self, boolean=True):
        """print the current menu to the screen"""
        self.render_thread.fill_screen(BACKGROUND)
        # TODO add game surface here
        # surface = pygame.Surface((screen_x, screen_y))
        if self.bg_image.get_width() is not self.screen_x or self.bg_image.get_height() is not self.screen_y:
            self.bg_image = pygame.transform.scale(self.bg_image, (self.screen_x, self.screen_y))
        # save this as background surface for dirty rects
        self.render_thread.bg_surface = self.bg_image
        self.render_thread.blit(self.bg_image, (0, 0))

        if boolean:
            self.in_menu = True
            self.current_menu.print_menu(self.menu_pos, self.menu_pos, True)
            self.render_thread.blit(self.current_menu.surface, None, True)
            # render_thread.add_rect_to_update(rects)
        else:
            self.in_menu = False
            self.menu_pos = 1
        # draw the selected surface to the screen
        self.render_thread.refresh_screen(True)

    def navigate_menu(self, old_pos, complete=False):
        """helps rerendering the changed menu items for partial screen updates"""
        rects = self.current_menu.print_menu(self.menu_pos, old_pos, complete)
        self.render_thread.blit(self.current_menu.surface, None, True)
        self.render_thread.add_rect_to_update(rects, self.current_menu.surface, None, True)

    def do_menu_action(self):
        """try to evaluate if a menu action is either a sub-menu or a function to call"""
        try:
            action = self.current_menu.get_menu_item(self.menu_pos).action
            if isinstance(action, Menu):
                self.set_current_menu(action)
            else:
                eval('self.%s' % action)
        except TypeError:
            # don't crash on wrong actions, the menu will stay up and nothing will happen
            pass

    def set_resolution(self, width, height, restart=False):
        """set the main screen/surface resolution

        Args:
            width (int): new width
            height (int): new height
            restart (bool): restart this process for a clean initialization
        """
        self.screen_x = width
        self.screen_y = height

        if restart:
            '''save changed settings to disk and restart this program'''
            self.write_settings()
            self.restart_program()
        else:
            self.render_thread.set_resolution(self.screen_x, self.screen_y)

    def switch_fullscreen(self):
        """switch between windowed and fullscreen mode"""
        self.fullscreen = False if self.fullscreen else True
        '''save changed settings to disk and restart this program'''
        self.write_settings()
        self.restart_program()

    def switch_show_fps(self):
        """switch fps overlay on/off"""
        new = False if self.render_thread.show_framerate else True
        self.render_thread.show_framerate = new
        self.current_menu.get_menu_item(self.menu_pos).text = self.get_button_text("Show FPS", new)
        self.show_menu(True)

    def switch_fs_resolution(self):
        """switch between windowed and fullscreen mode"""
        new = False if self.switch_resolution else True
        self.switch_resolution = new
        '''save changed settings to disk'''
        self.write_settings()
        if self.fullscreen:
            '''and restart this program'''
            self.restart_program()
        else:
            self.current_menu.get_menu_item(self.menu_pos).text = self.get_button_text("Switch Resolution", new)
            self.show_menu(True)

    def get_button_text(self, text, text_val):
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
            return "".join([">" if i < vol else " " for i in range(10)])

        def bool_to_string(boolean):
            """helper function for the MenuItems containing booleans in their name"""
            return "on" if boolean else "off"

        info_str = False

        if isinstance(text_val, bool):
            text_val = bool_to_string(text_val)
            if text is "Music":
                info_str = print_audio_volume_bar(self.music_thread.music_volume)
            elif text is "Sounds":
                info_str = print_audio_volume_bar(self.music_thread.sfx_volume)
        elif isinstance(text_val, str):
            if text is "Resolution":
                return '{:<24s} {:>10s}'.format(text, text_val)

        if info_str:
            return '{:<10s} {:<4s} {:12s}'.format(text, text_val, info_str)
        else:
            return '{:<28s} {:>6s}'.format(text, text_val)

    def switch_audio_volume(self, num, change):
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
            """turn music on or off"""
            self.play_music = self.music_thread.play_music = m_bol

        def set_music_vol(m_vol):
            """set music volume"""
            self.vol_music = self.music_thread.music_volume = m_vol

        def set_sfx(s_bol):
            """turn sfx on or off"""
            self.play_sfx = self.music_thread.play_sfx = s_bol

        def set_sfx_vol(s_vol):
            """set sfx volume"""
            self.vol_sfx = self.music_thread.sfx_volume = s_vol

        # to store the settings so they can be saved on exit
        item = self.current_menu.get_menu_item(self.menu_pos)
        txt = bol = vol = None
        if num is 1:
            vol = self.music_thread.music_volume
        elif num is 2:
            vol = self.music_thread.sfx_volume

        if 0 <= vol + change <= 10:
            '''in/decrease the volume'''
            old_vol = vol
            vol += change
            if num is 1:
                txt = "Music"
                bol = self.music_thread.play_music
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
                bol = self.music_thread.play_sfx
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
            item.text = self.get_button_text(txt, bol)
            '''and refresh the menu'''
            self.show_menu(True)

    def quit_game(self, shutdown=True):
        """quit the game"""
        self.write_settings()
        self.render_thread.stop_thread()
        self.music_thread.stop_thread()
        pygame.quit()
        if shutdown:
            exit()

    def restart_program(self):
        """Restarts the current program"""
        self.quit_game(False)
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def start_game(self):
        """start the game"""
        # Main loop relevant vars
        clock = pygame.time.Clock()

        # switch music (test)
        self.music_thread.background_music = ('summers_end_acoustic.aif', 0)
        # we should probably save all game sounds as variables
        sound_shoot = pygame.mixer.Sound(self.music_thread.get_full_path_sfx('9_mm_gunshot-mike-koenig-123.wav'))

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.quit_game()
                elif event.type == KEYDOWN:
                    key = event.key
                    '''key pressing events'''
                    if self.in_menu:
                        """key settings if the main menu is active"""
                        if key == K_ESCAPE:
                            back_item = self.current_menu.get_menu_item(self.current_menu.length - 1).action
                            if isinstance(back_item, Menu):
                                self.set_current_menu(back_item)
                            else:
                                self.show_menu(False)
                        elif key == K_RETURN:
                            self.do_menu_action()
                        elif key == K_UP:
                            if 1 < self.menu_pos:
                                self.menu_pos -= 1
                                self.navigate_menu(self.menu_pos + 1)
                        elif key == K_DOWN:
                            if self.menu_pos < self.current_menu.length - 1:
                                self.menu_pos += 1
                                self.navigate_menu(self.menu_pos - 1)
                        elif key == K_LEFT:
                            action = self.current_menu.get_menu_item(self.menu_pos).action
                            if action == 'switch_audio_volume(1, 0)':
                                self.switch_audio_volume(1, -1)
                            elif action == 'switch_audio_volume(2, 0)':
                                self.switch_audio_volume(2, -1)
                        elif key == K_RIGHT:
                            action = self.current_menu.get_menu_item(self.menu_pos).action
                            if action == 'switch_audio_volume(1, 0)':
                                self.switch_audio_volume(1, 1)
                            elif action == 'switch_audio_volume(2, 0)':
                                self.switch_audio_volume(2, 1)
                        elif key == K_SPACE:
                            self.music_thread.play_sound(sound_shoot)
                        elif key == K_LSHIFT:
                            self.music_thread.play_sound('unscrew_lightbulb-mike-koenig.wav')
                    else:
                        """controls and key settings if the game is in foreground"""
                        if key == K_ESCAPE:
                            self.show_menu(True)
                        '''
                        if key == (p1_left or p1_right or p1_up or p1_down or p2_left or p2_right or p2_up or p2_down):
                            # TODO move player 1/2 direction
                            return pass

                        elif key == (p1_action_left or p1_action_right or p2_action_left or p2_action_right):
                            # TODO action player 1/2 left/right
                            return pass

                        elif key == (p1_interact or p1_taunt or p2_interact or p2_taunt):
                            # TODO taunt/interact player 1/2
                            return pass
                        '''

            # save cpu resources
            clock.tick(self.fps)


if __name__ == "__main__":
    pyrunner = PyRunner()
    # start the 4 in a row game
    pyrunner.start_game()
