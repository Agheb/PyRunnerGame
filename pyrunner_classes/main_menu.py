#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
# universal imports
import pygame
from pygame.locals import *
from .menu import Menu, MenuItem
from .constants import *


class MainMenu(object):
    """PyRunners main menu"""

    def __init__(self, main):
        self.main = main
        self.config = self.main.config
        self.render_thread = self.main.render_thread
        self.music_thread = self.main.music_thread
        self.bg_image = self.main.bg_image
        self.menu_pos = 1
        self.in_menu = True
        self.current_menu = None
        self.init_menu()

    def key_actions(self, key):
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
        menu_main.add_menu_item(MenuItem(self.config.name, None, h1_size))
        # new game menu
        menu_new_game = Menu(surface, menu_main, item_size)
        # heading
        menu_new_game.add_menu_item(MenuItem("Start Game", None, h2_size))
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
        # finish top menu with sub menus
        menu_new_game.add_menu_item(MenuItem("Singleplayer", menu_ng_singleplayer, item_size))
        menu_new_game.add_menu_item(MenuItem("Multiplayer", menu_ng_multiplayer, item_size))
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
        menu_s_video.add_menu_item(MenuItem(self.get_button_text("Fullscreen", self.config.fullscreen),
                                            'switch_fullscreen()', item_size))
        menu_s_video_switch_res = self.get_button_text("Switch Resolution", self.config.switch_resolution)
        menu_s_video.add_menu_item(MenuItem(menu_s_video_switch_res, 'switch_fs_resolution()', item_size))
        # resolutions
        menu_s_v_resolution = Menu(surface, menu_s_video, item_size)
        menu_s_v_resolution.add_menu_item(MenuItem("Video Resolution", None, h2_size))
        for res in self.render_thread.display_modes:
            width, height = res
            res_name = str(width) + "x" + str(height)
            func_name = "set_resolution(" + str(width) + ", " + str(height) + ", True)"
            menu_s_v_resolution.add_menu_item(MenuItem(res_name, func_name, item_size))
        res_name = str(self.config.screen_x) + "x" + str(self.config.screen_y)
        menu_s_video.add_menu_item(
            MenuItem(self.get_button_text("Resolution", res_name), menu_s_v_resolution, item_size))
        menu_s_video_show_fps = self.get_button_text("Show FPS", self.render_thread.show_framerate)
        menu_s_video.add_menu_item(MenuItem(menu_s_video_show_fps, 'switch_show_fps()', item_size))
        menu_controls = Menu(surface, menu_settings, item_size)
        menu_controls.add_menu_item(MenuItem("Controls", None, h2_size))
        menu_controls.add_menu_item(MenuItem("Player 1", None, item_size))
        menu_controls.add_menu_item(MenuItem("Player 2", None, item_size))
        '''complete the settings menu at the end to store the up to date objects'''
        menu_settings.add_menu_item(MenuItem("Audio", menu_s_audio, item_size))
        menu_settings.add_menu_item(MenuItem("Controls", menu_controls, item_size))
        menu_settings.add_menu_item(MenuItem("Video", menu_s_video, item_size))
        '''complete main menu at the end to store the up to date objects'''
        menu_main.add_menu_item(MenuItem("Start Game", menu_new_game, item_size))
        menu_main.add_menu_item(MenuItem("Settings", menu_settings, item_size))
        menu_main.add_menu_item(MenuItem("Exit", 'main.quit_game()', item_size))

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
        if self.bg_image.get_width() is not self.config.screen_x or self.bg_image.get_height() is not self.config.screen_y:
            self.bg_image = pygame.transform.scale(self.bg_image, (self.config.screen_x, self.config.screen_y))
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
                if action:
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
        self.config.screen_x = width
        self.config.screen_y = height

        if restart:
            '''save changed settings to disk and restart this program'''
            self.config.write_settings()
            self.main.restart_program()
        else:
            self.render_thread.set_resolution(self.config.screen_x, self.config.screen_y)

    def switch_fullscreen(self):
        """switch between windowed and fullscreen mode"""
        self.config.fullscreen = False if self.config.fullscreen else True
        '''save changed settings to disk and restart this program'''
        self.config.write_settings()
        self.main.restart_program()

    def switch_show_fps(self):
        """switch fps overlay on/off"""
        new = False if self.render_thread.show_framerate else True
        self.render_thread.show_framerate = new
        self.current_menu.get_menu_item(self.menu_pos).text = self.get_button_text("Show FPS", new)
        self.show_menu(True)

    def switch_fs_resolution(self):
        """switch between windowed and fullscreen mode"""
        new = False if self.config.switch_resolution else True
        self.config.switch_resolution = new
        '''save changed settings to disk'''
        self.config.write_settings()
        if self.config.fullscreen:
            '''and restart this program'''
            self.main.restart_program()
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

        def set_music(val):
            """turn music on or off"""
            self.config.play_music = self.music_thread.play_music = val
            return val

        def set_music_vol(val):
            """set music volume"""
            self.config.vol_music = self.music_thread.music_volume = val
            return val

        def set_sfx(val):
            """turn sfx on or off"""
            self.config.play_sfx = self.music_thread.play_sfx = val
            return val

        def set_sfx_vol(val):
            """set sfx volume"""
            self.config.vol_sfx = self.music_thread.sfx_volume = val
            return val

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
