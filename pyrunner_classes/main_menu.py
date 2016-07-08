#!/usr/bin/python
# -*- coding: utf-8 -*-
"""creates the main menu and handles all menu actions"""
# Python 2 related fixes
from __future__ import division
# universal imports
import pygame
from pygame.locals import *
from time import sleep
from .menu import Menu, MenuItem
from .level import Level


class MainMenu(object):
    """initialize PyRunners main menu, save all required objects"""

    def __init__(self, main, network_connector):
        self.main = main
        self.config = self.main.config
        self.render_thread = self.main.render_thread
        self.network_connector = network_connector
        self.music_thread = self.main.music_thread
        self.bg_image = self.main.bg_surface
        self.menu_pos = 1
        self.in_menu = True
        self.current_menu = None
        self.main_menu = None
        self.game_over = None
        self.network = None
        self.surface = None
        self.configure_keys = False
        self.configure_js = False
        self.config_keys_player = None
        self.config_keys_action = None
        self.m_settings_cp1 = None
        self.menu_config_p1 = None
        self.m_settings_js1 = None
        self.m_settings_cp2 = None
        self.menu_config_p2 = None
        self.m_settings_js2 = None
        # regular font sizes
        self.h1_size = 72
        self.h2_size = 48
        self.item_size = 36
        self.ratio = 1

        '''initialize the menu'''
        self.init_menu()

    def key_actions(self, key):
        """key settings if the main menu is active"""
        if self.configure_keys:
            self.set_keyboard_controls(key)
        else:
            if key == K_ESCAPE:
                if self.current_menu.parent:
                    self.set_current_menu(self.current_menu.parent)
                elif not self.main.game_over and Level.players:
                    self.show_menu(False)
            elif key == K_RETURN:
                self.current_menu.get_item(self.menu_pos).do_action()
            elif key == K_UP:
                if 1 < self.menu_pos:
                    self.menu_pos -= 1
                    self.navigate_menu(self.menu_pos + 1)
            elif key == K_DOWN:
                if self.menu_pos < self.current_menu.length - 1:
                    self.menu_pos += 1
                    self.navigate_menu(self.menu_pos - 1)
            elif key == K_LEFT:
                name = self.current_menu.get_item(self.menu_pos).name
                if name == "Music":
                    self.switch_audio_volume((1, -1))
                elif name == "Sounds":
                    self.switch_audio_volume((2, -1))
            elif key == K_RIGHT:
                name = self.current_menu.get_item(self.menu_pos).name
                if name == "Music":
                    self.switch_audio_volume((1, 1))
                elif name == "Sounds":
                    self.switch_audio_volume((2, 1))

    def joystick_actions(self, event):
        """use a gamepad or joystick to navigate the menu"""
        if self.configure_js:
            self.set_joystick_controls(event)
        else:
            string = str(event.__dict__)
            if self.config.p1_use_joystick:
                self.key_actions(self.config.p1_menu_map.get(string))
            elif self.config.p2_use_joystick:
                self.key_actions(self.config.p2_menu_map.get(string))

    def init_menu(self):
        """initialize the whole main menu structure

        Cave: menus need to be saved in the reverse order (bottom to top) so that
              the top menus contain all up to date sub-menu objects
        """
        s_width = (self.render_thread.screen.get_width() // 16) * 9
        s_height = (self.render_thread.screen.get_height() // 9) * 5
        surface = pygame.Surface((s_width, s_height))
        # regular font sizes
        h1_size = self.h1_size
        h2_size = self.h2_size
        item_size = self.item_size
        '''calculate the ratio to adjust font sizes accordingly'''
        ratio = Menu.calc_font_size(surface, h1_size, item_size)
        h1_size = int(h1_size * ratio)
        h2_size = int(h2_size * ratio)
        item_size = int(item_size * ratio)
        font_size = h1_size, h2_size, item_size
        '''first create the root menu'''
        menu_main = Menu(self, self.config.name, surface, None, font_size)

        '''New Game Menu'''
        menu_main.add_item(MenuItem("Start Game", self.network_connector.start_local_game))

        '''New Game / Single Player'''
        # m_game.add_item(MenuItem("Select Level", None))
        # m_game.add_item(MenuItem("Game Settings", None))

        '''New Game / Multiplayer'''
        m_game_mp = menu_main.add_submenu("Multiplayer")
        m_game_mp.add_item(MenuItem("Local Game", None))
        m_game_mp.add_item(MenuItem("Start Server", self.network_connector.start_server_prompt))
        m_game_mp.add_item(MenuItem("Join Server", self.network_connector.join_server_menu))
        m_game_mp.add_item(MenuItem("Game Settings", None))

        '''Settings'''
        m_settings = menu_main.add_submenu("Settings")

        '''Settings / Audio'''
        m_settings_audio = m_settings.add_submenu("Audio Settings")
        m_settings_audio.add_item(MenuItem("Music", self.switch_audio_volume, vars=(1, 0),
                                           val=self.music_thread.play_music, bar=self.music_thread.music_volume))
        m_settings_audio.add_item(MenuItem("Sounds", self.switch_audio_volume, vars=(2, 0),
                                           val=self.music_thread.play_sfx, bar=self.music_thread.sfx_volume))

        '''Settings / Video'''
        m_settings_video = m_settings.add_submenu("Video Settings")
        m_settings_video.add_item(MenuItem("Fullscreen", self.switch_fullscreen, val=self.config.fullscreen))
        m_settings_video.add_item(MenuItem("Switch Resolution", self.switch_fs_resolution,
                                           val=self.config.switch_resolution))
        res_name = "%sx%s" % (self.config.screen_x, self.config.screen_y)
        m_settings_video_res = m_settings_video.add_submenu('{:<24s} {:>10s}'.format("Resolution", res_name))
        m_settings_video.add_item(MenuItem("Show FPS", self.switch_show_fps, val=self.render_thread.show_framerate))

        '''Settings / Video / Resolutions'''
        for res in self.render_thread.display_modes:
            width, height = res
            res_name = str(width) + "x" + str(height)
            m_settings_video_res.add_item(MenuItem(res_name, self.set_resolution, vars=(width, height, True)))

        '''Settings / Controls'''
        m_settings_controls = m_settings.add_submenu("Controls")
        m_settings_cp1 = m_settings_controls.add_submenu("Player 1")
        m_settings_cp2 = m_settings_controls.add_submenu("Player 2")

        '''joystick/gamepad setup'''
        if pygame.joystick.get_count() > 0:
            joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

            menu_config_joystick_p1 = m_settings_cp1.add_submenu("Configure Joystick")
            menu_config_joystick_p2 = m_settings_cp2.add_submenu("Configure Joystick")
            for jid, js in enumerate(joysticks):
                js.init()
                js_name = js.get_name()
                js_axes = js.get_numaxes()
                js_balls = js.get_numballs()
                js_buttons = js.get_numbuttons()
                js_hats = js.get_numhats()
                js_info = "ID: %(jid)s | Axes: %(js_axes)s | Balls: %(js_balls)s" % locals()
                js_info2 = "Buttons: %(js_buttons)s | Hats: %(js_hats)s" % locals()
                '''Add the joystick to the controls section of player 1'''
                menu_js_1 = menu_config_joystick_p1.add_submenu(js_name)
                menu_js_1.add_item(MenuItem(js_info))
                menu_js_1.add_item(MenuItem(js_info2))
                menu_js_1.add_item(MenuItem("Use this Device for Player 1", self.use_joystick,
                                            vars=(1, js_name, jid), val=self.config.p1_use_joystick))
                '''and to the controls section of player 2'''
                menu_js_2 = menu_config_joystick_p2.add_submenu(js_name)
                menu_js_2.add_item(MenuItem(js_info))
                menu_js_2.add_item(MenuItem(js_info2))
                menu_js_2.add_item(MenuItem("Use this Device for Player 2", self.use_joystick,
                                            vars=(2, js_name, jid), val=self.config.p2_use_joystick))

            '''joystick key setup'''
            menu_config_js_p1 = menu_config_joystick_p1.add_submenu("Configure Joystick")
            menu_config_js_p1.add_item(MenuItem("Left", self.configure_js_controls,
                                                vars=(1, "Left"), val=self.config.p1_js_left))
            menu_config_js_p1.add_item(MenuItem("Right", self.configure_js_controls,
                                                vars=(1, "Right"), val=self.config.p1_js_right))
            menu_config_js_p1.add_item(MenuItem("Up", self.configure_js_controls,
                                                vars=(1, "Up"), val=self.config.p1_js_up))
            menu_config_js_p1.add_item(MenuItem("Down", self.configure_js_controls,
                                                vars=(1, "Down"), val=self.config.p1_js_down))
            menu_config_js_p1.add_item(MenuItem("Dig Left", self.configure_js_controls,
                                                vars=(1, "Dig Left"), val=self.config.p1_js_action_l))
            menu_config_js_p1.add_item(MenuItem("Dig Right", self.configure_js_controls,
                                                vars=(1, "Dig Right"), val=self.config.p1_js_action_r))
            menu_config_js_p1.add_item(MenuItem("Interact", self.configure_js_controls,
                                                vars=(1, "Interact"), val=self.config.p1_js_interact))
            menu_config_js_p1.add_item(MenuItem("Taunt", self.configure_js_controls,
                                                vars=(1, "Taunt"), val=self.config.p1_js_taunt))
            menu_config_js_p1.add_item(MenuItem("Accept", self.configure_js_controls,
                                                vars=(1, "Accept"), val=self.config.p1_js_accept))
            menu_config_js_p1.add_item(MenuItem("Cancel", self.configure_js_controls,
                                                vars=(1, "Cancel"), val=self.config.p1_js_cancel))

            menu_config_js_p2 = menu_config_joystick_p2.add_submenu("Configure Joystick")
            menu_config_js_p2.add_item(MenuItem("Left", self.configure_js_controls,
                                                vars=(2, "Left"), val=self.config.p2_js_left))
            menu_config_js_p2.add_item(MenuItem("Right", self.configure_js_controls,
                                                vars=(2, "Right"), val=self.config.p2_js_right))
            menu_config_js_p2.add_item(MenuItem("Up", self.configure_js_controls,
                                                vars=(2, "Up"), val=self.config.p2_js_up))
            menu_config_js_p2.add_item(MenuItem("Down", self.configure_js_controls,
                                                vars=(2, "Down"), val=self.config.p2_js_down))
            menu_config_js_p2.add_item(MenuItem("Dig Left", self.configure_js_controls,
                                                vars=(2, "Dig Left"), val=self.config.p2_js_action_l))
            menu_config_js_p2.add_item(MenuItem("Dig Right", self.configure_js_controls,
                                                vars=(2, "Dig Right"), val=self.config.p2_js_action_r))
            menu_config_js_p2.add_item(MenuItem("Interact", self.configure_js_controls,
                                                vars=(2, "Interact"), val=self.config.p2_js_interact))
            menu_config_js_p2.add_item(MenuItem("Taunt", self.configure_js_controls,
                                                vars=(2, "Taunt"), val=self.config.p2_js_taunt))
            menu_config_js_p2.add_item(MenuItem("Accept", self.configure_js_controls,
                                                vars=(2, "Accept"), val=self.config.p2_js_accept))
            menu_config_js_p2.add_item(MenuItem("Cancel", self.configure_js_controls,
                                                vars=(2, "Cancel"), val=self.config.p2_js_cancel))

        '''Settings / Controls / Player 1'''
        m_settings_cp1.add_item(MenuItem("Left", self.configure_key_controls,
                                         vars=(1, "Left"), val=self.config.p1_left))
        m_settings_cp1.add_item(MenuItem("Right", self.configure_key_controls,
                                         vars=(1, "Right"), val=self.config.p1_right))
        m_settings_cp1.add_item(MenuItem("Up", self.configure_key_controls,
                                         vars=(1, "Up"), val=self.config.p1_up))
        m_settings_cp1.add_item(MenuItem("Down", self.configure_key_controls,
                                         vars=(1, "Down"), val=self.config.p1_down))
        m_settings_cp1.add_item(MenuItem("Dig Left", self.configure_key_controls,
                                         vars=(1, "Dig Left"), val=self.config.p1_action_l))
        m_settings_cp1.add_item(MenuItem("Dig Right", self.configure_key_controls,
                                         vars=(1, "Dig Right"), val=self.config.p1_action_r))
        m_settings_cp1.add_item(MenuItem("Interact", self.configure_key_controls,
                                         vars=(1, "Interact"), val=self.config.p1_interact))
        m_settings_cp1.add_item(MenuItem("Taunt", self.configure_key_controls,
                                         vars=(1, "Taunt"), val=self.config.p1_taunt))

        '''Settings / Controls / Player 2'''
        m_settings_cp2.add_item(MenuItem("Left", self.configure_key_controls,
                                         vars=(2, "Left"), val=self.config.p2_left))
        m_settings_cp2.add_item(MenuItem("Right", self.configure_key_controls,
                                         vars=(2, "Right"), val=self.config.p2_right))
        m_settings_cp2.add_item(MenuItem("Up", self.configure_key_controls,
                                         vars=(2, "Up"), val=self.config.p2_up))
        m_settings_cp2.add_item(MenuItem("Down", self.configure_key_controls,
                                         vars=(2, "Down"), val=self.config.p2_down))
        m_settings_cp2.add_item(MenuItem("Dig Left", self.configure_key_controls,
                                         vars=(2, "Dig Left"), val=self.config.p2_action_l))
        m_settings_cp2.add_item(MenuItem("Dig Right", self.configure_key_controls,
                                         vars=(2, "Dig Right"), val=self.config.p2_action_r))
        m_settings_cp2.add_item(MenuItem("Interact", self.configure_key_controls,
                                         vars=(2, "Interact"), val=self.config.p2_interact))
        m_settings_cp2.add_item(MenuItem("Taunt", self.configure_key_controls,
                                         vars=(2, "Taunt"), val=self.config.p2_taunt))

        '''Exit'''
        menu_main.add_item(MenuItem("Exit", self.main.quit_game))

        '''special purpose (hidden) menus'''
        '''game over menu'''
        menu_game_over = menu_main.add_submenu("Game Over", True)
        '''network related menu'''
        menu_network_browser = m_game_mp.add_submenu("Join Server", True)

        '''save the menus'''
        self.m_settings_cp1 = m_settings_cp1
        self.m_settings_cp2 = m_settings_cp2
        self.game_over = menu_game_over
        self.network = menu_network_browser
        self.main_menu = menu_main

        '''show the main menu'''
        self.set_current_menu(self.main_menu)

    def set_current_menu(self, new_menu):
        """switch menu level

        Args:
            new_menu (Menu): the (sub)menu to switch to
        """
        self.current_menu = new_menu
        self.menu_pos = 1
        self.show_menu()

    def show_menu(self, show=True):
        """print the current menu to the screen"""
        self.in_menu = show

        if self.in_menu:
            self.render_thread.blit(self.main.level.background, None, True)
            rects, self.menu_pos = self.current_menu.print_menu(self.menu_pos, self.menu_pos, True)
            self.render_thread.blit(self.current_menu.surface, None, True)
        else:
            self.menu_pos = 1
            self.render_thread.blit(self.main.level.surface, None, True)

        '''avoid screen flickering'''
        sleep(0.1)
        # draw the selected surface to the screen
        self.render_thread.refresh_screen(True)

    def navigate_menu(self, old_pos, complete=False):
        """helps rerendering the changed menu items for partial screen updates"""
        rects, self.menu_pos = self.current_menu.print_menu(self.menu_pos, old_pos, complete)
        self.render_thread.blit(self.current_menu.surface, None, True)
        self.render_thread.add_rect_to_update(rects, self.current_menu.surface, None, True)

    def reload_level(self):
        """retry/reload the current level"""
        self.main.load_level()
        self.current_menu = self.main_menu
        self.menu_pos = 1
        self.show_menu(False)

    def use_joystick(self, player_jsname):
        """turn usage of a joystick / gamepad on / off per player"""
        player, js_name, jid = player_jsname

        if player is 1:
            new_val = True if not self.config.p1_use_joystick else False
            if self.config.p2_use_joystick:
                if self.config.p2_js_name == js_name:
                    self.current_menu.print_error("This device is already used by Player 2")
                    return
            self.config.p1_use_joystick = new_val
            self.config.p1_js_name = js_name
            self.config.p1_js_id = jid
        else:
            new_val = True if not self.config.p2_use_joystick else False
            if self.config.p1_use_joystick:
                if self.config.p1_js_name == js_name:
                    self.current_menu.print_error("This device is already used by Player 1")
                    return
            self.config.p2_use_joystick = new_val
            self.config.p2_js_name = js_name
            self.config.p2_js_id = jid

        self.current_menu.get_item(self.menu_pos).val = new_val
        self.navigate_menu(self.menu_pos)

    def configure_key_controls(self, player_action):
        """decide what should be configured"""
        self.config_keys_player, self.config_keys_action = player_action

        self.current_menu.get_item(self.menu_pos).val = "Press any key"
        self.navigate_menu(self.menu_pos)
        self.configure_keys = True

    def set_keyboard_controls(self, key):
        """configure the player controls"""
        player, action = self.config_keys_player, self.config_keys_action
        new_key = pygame.key.name(key)

        if player is 1:
            if action == "Left":
                self.config.p1_left = key
            elif action == "Right":
                self.config.p1_right = key
            elif action == "Up":
                self.config.p1_up = key
            elif action == "Down":
                self.config.p1_down = key
            elif action == "Dig Left":
                self.config.p1_action_l = key
            elif action == "Dig Right":
                self.config.p1_action_r = key
            elif action == "Interact":
                self.config.p1_interact = key
            elif action == "Taunt":
                self.config.p1_taunt = key

        elif player is 2:
            if action == "Left":
                self.config.p2_left = key
            elif action == "Right":
                self.config.p2_right = key
            elif action == "Up":
                self.config.p2_up = key
            elif action == "Down":
                self.config.p2_down = key
            elif action == "Dig Left":
                self.config.p2_action_l = key
            elif action == "Dig Right":
                self.config.p2_action_r = key
            elif action == "Interact":
                self.config.p2_interact = key
            elif action == "Taunt":
                self.config.p2_taunt = key

        self.current_menu.get_item(self.menu_pos).val = new_key
        self.navigate_menu(self.menu_pos)
        self.configure_keys = False

    def configure_js_controls(self, player_action):
        """decide what should be configured"""
        self.config_keys_player, self.config_keys_action = player_action

        self.current_menu.get_item(self.menu_pos).val = "Press any Button"
        self.navigate_menu(self.menu_pos)
        self.configure_js = True

    def set_joystick_controls(self, event):
        """configure the player controls"""
        player, action = self.config_keys_player, self.config_keys_action
        new_key = None
        jid = event.__dict__["joy"]

        if event.type == JOYAXISMOTION:
            axis = event.__dict__["axis"]
            val = event.__dict__["value"]
            val = -1 if val < 0 else 1
            new_key = "Axis %s %s" % (axis, val)
        elif event.type == JOYBALLMOTION:
            pass
        elif event.type == JOYBUTTONDOWN:
            new_key = "Button %s" % event.__dict__["button"]
        elif event.type == JOYHATMOTION:
            hat = event.__dict__["hat"]
            val = event.__dict__["value"]
            new_key = "Hat %s %s" % (hat, val)

        if player is 1:
            if jid != self.config.p1_js_id:
                print("Error: wrong joystick id %s" % jid)
                return

            '''ignore input from other devices'''
            if action == "Left":
                self.config.p1_js_left = new_key
            elif action == "Right":
                self.config.p1_js_right = new_key
            elif action == "Up":
                self.config.p1_js_up = new_key
            elif action == "Down":
                self.config.p1_js_down = new_key
            elif action == "Dig Left":
                self.config.p1_js_action_l = new_key
            elif action == "Dig Right":
                self.config.p1_js_action_r = new_key
            elif action == "Interact":
                self.config.p1_js_interact = new_key
            elif action == "Taunt":
                self.config.p1_js_taunt = new_key
            elif action == "Accept":
                self.config.p1_js_accept = new_key
            elif action == "Cancel":
                self.config.p1_js_cancel = new_key

        elif player is 2:
            if action == "Left":
                self.config.p2_js_left = new_key
            elif action == "Right":
                self.config.p2_js_right = new_key
            elif action == "Up":
                self.config.p2_js_up = new_key
            elif action == "Down":
                self.config.p2_js_down = new_key
            elif action == "Dig Left":
                self.config.p2_js_action_l = new_key
            elif action == "Dig Right":
                self.config.p2_js_action_r = new_key
            elif action == "Interact":
                self.config.p2_js_interact = new_key
            elif action == "Taunt":
                self.config.p2_js_taunt = new_key
            elif action == "Accept":
                self.config.p2_js_accept = new_key
            elif action == "Cancel":
                self.config.p2_js_cancel = new_key

        self.current_menu.get_item(self.menu_pos).val = new_key
        '''reinit the maps if there are changes made to the config'''
        self.config.setup_joystick()
        self.navigate_menu(self.menu_pos)
        self.configure_js = False

    def set_resolution(self, var):
        """set the main screen/surface resolution

        Args:
            var (width, height, restart):
                width (int): new width
                height (int): new height
                restart (bool): restart this process for a clean initialization
        """
        width, height, restart = var
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
        self.current_menu.get_item(self.menu_pos).val = new
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
            self.current_menu.get_item(self.menu_pos).val = new
            self.show_menu(True)

    def switch_audio_volume(self, var):
        """Function to switch the Music and Sound FX volume with the left/right keys
           when hovering the Music or Sound FX on/off Menu Item

        Args:
            var (num, change):
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

        num, change = var
        # to store the settings so they can be saved on exit
        item = self.current_menu.get_item(self.menu_pos)
        vol = bol = None
        if num is 1:
            vol = self.music_thread.music_volume
        elif num is 2:
            vol = self.music_thread.sfx_volume

        if 0 <= vol + change <= 10:
            '''in/decrease the volume'''
            old_vol = vol
            vol += change
            if num is 1:
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
                        vol = set_music_vol(1)
            elif num is 2:
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
                        vol = set_sfx_vol(1)
            '''update the menu button'''
            item.bar = vol
            item.val = bol
            item.set_rect()
            '''and refresh the menu'''
            self.show_menu(True)
