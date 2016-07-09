#!/usr/bin/python
# -*- coding: utf-8 -*-
"""reads and writes the game configuration to the disk"""
# Python 2 related fixes
from __future__ import division
try:
    # noinspection PyUnresolvedReferences
    import configparser    # Python 3
except ImportError:
    import ConfigParser    # Python 2
# PyGame
from pygame.locals import *
from ast import literal_eval as make_tuple

'''constants'''
NAME = "pyRunner"
CONFIG = "resources/config.cfg"
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
_CONF_CONT_P1 = "Player 1 Controls"
_CONF_CONT_P2 = "Player 2 Controls"
_CONF_CONT_P1_JS = "Player 1 Joystick/Gamepad"
_CONF_CONT_P2_JS = "Player 2 Joystick/Gamepad"
_CONF_CONT_USE_JS = "use joystick/gamepad"
_CONF_CONT_NAME_JS = "device name"
_CONF_CONT_ID_JS = "device id"
_CONF_CONT_LEFT = "left"
_CONF_CONT_RIGHT = "right"
_CONF_CONT_UP = "up"
_CONF_CONT_DOWN = "down"
_CONF_CONT_AL = "action left"
_CONF_CONT_AR = "action right"
_CONF_CONT_INT = "interact"
_CONF_CONT_TAUNT = "taunt"
_CONF_CONT_JUMP = "jump"
_CONF_CONT_ACCEPT_JS = "accept"
_CONF_CONT_CANCEL_JS = "escape"


class MainConfig(object):
    """parse all relevant game configuration values from the config.cfg"""

    def __init__(self):
        self.name = NAME
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
        '''controls'''
        self.p1_key_map = None
        self.p1_menu_map = None
        self.p2_key_map = None
        self.p2_menu_map = None
        '''controls for player 1'''
        self.p1_left = None
        self.p1_right = None
        self.p1_up = None
        self.p1_down = None
        self.p1_action_l = None
        self.p1_action_r = None
        self.p1_interact = None
        self.p1_taunt = None
        '''joystick / gamepad'''
        self.p1_use_joystick = None
        self.p1_js_name = None
        self.p1_js_id = None
        self.p1_js_left = None
        self.p1_js_right = None
        self.p1_js_up = None
        self.p1_js_down = None
        self.p1_js_stop = None
        self.p1_js_action_l = None
        self.p1_js_action_r = None
        self.p1_js_interact = None
        self.p1_js_taunt = None
        self.p1_js_accept = None    # ~= Return
        self.p1_js_cancel = None    # ~= ESC
        '''controls for player 2'''
        self.p2_left = None
        self.p2_right = None
        self.p2_up = None
        self.p2_down = None
        self.p2_action_l = None
        self.p2_action_r = None
        self.p2_interact = None
        self.p2_taunt = None
        '''joystick / gamepad'''
        self.p2_use_joystick = None
        self.p2_js_name = None
        self.p2_js_id = None
        self.p2_js_left = None
        self.p2_js_right = None
        self.p2_js_up = None
        self.p2_js_down = None
        self.p2_js_stop = None
        self.p2_js_action_l = None
        self.p2_js_action_r = None
        self.p2_js_interact = None
        self.p2_js_taunt = None
        self.p2_js_accept = None  # ~= Return
        self.p2_js_cancel = None  # ~= ESC
        '''read the configuration file to initialize above variables'''
        self.config_parser = self.init_config_parser()
        self.read_settings()

        self.setup_joystick()

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
        except NameError:
            raise

        try:
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
            '''controls for player 1'''
            self.p1_left = config.getint(_CONF_CONT_P1, _CONF_CONT_LEFT)
            self.p1_right = config.getint(_CONF_CONT_P1, _CONF_CONT_RIGHT)
            self.p1_up = config.getint(_CONF_CONT_P1, _CONF_CONT_UP)
            self.p1_down = config.getint(_CONF_CONT_P1, _CONF_CONT_DOWN)
            self.p1_action_l = config.getint(_CONF_CONT_P1, _CONF_CONT_AL)
            self.p1_action_r = config.getint(_CONF_CONT_P1, _CONF_CONT_AR)
            self.p1_interact = config.getint(_CONF_CONT_P1, _CONF_CONT_INT)
            self.p1_taunt = config.getint(_CONF_CONT_P1, _CONF_CONT_TAUNT)
            self.p1_use_joystick = config.getboolean(_CONF_CONT_P1_JS, _CONF_CONT_USE_JS)
            if self.p1_use_joystick:
                self.p1_js_name = config.get(_CONF_CONT_P1_JS, _CONF_CONT_NAME_JS)
                self.p1_js_id = config.getint(_CONF_CONT_P1_JS, _CONF_CONT_ID_JS)
                self.p1_js_left = config.get(_CONF_CONT_P1_JS, _CONF_CONT_LEFT)
                self.p1_js_right = config.get(_CONF_CONT_P1_JS, _CONF_CONT_RIGHT)
                self.p1_js_up = config.get(_CONF_CONT_P1_JS, _CONF_CONT_UP)
                self.p1_js_down = config.get(_CONF_CONT_P1_JS, _CONF_CONT_DOWN)
                self.p1_js_action_l = config.get(_CONF_CONT_P1_JS, _CONF_CONT_AL)
                self.p1_js_action_r = config.get(_CONF_CONT_P1_JS, _CONF_CONT_AR)
                self.p1_js_interact = config.get(_CONF_CONT_P1_JS, _CONF_CONT_INT)
                self.p1_js_taunt = config.get(_CONF_CONT_P1_JS, _CONF_CONT_TAUNT)
                self.p1_js_accept = config.get(_CONF_CONT_P1_JS, _CONF_CONT_ACCEPT_JS)  # ~= Return
                self.p1_js_cancel = config.get(_CONF_CONT_P1_JS, _CONF_CONT_CANCEL_JS)  # ~= ESC
            '''controls for player 2'''
            self.p2_left = config.getint(_CONF_CONT_P2, _CONF_CONT_LEFT)
            self.p2_right = config.getint(_CONF_CONT_P2, _CONF_CONT_RIGHT)
            self.p2_up = config.getint(_CONF_CONT_P2, _CONF_CONT_UP)
            self.p2_down = config.getint(_CONF_CONT_P2, _CONF_CONT_DOWN)
            self.p2_action_l = config.getint(_CONF_CONT_P2, _CONF_CONT_AL)
            self.p2_action_r = config.getint(_CONF_CONT_P2, _CONF_CONT_AR)
            self.p2_interact = config.getint(_CONF_CONT_P2, _CONF_CONT_INT)
            self.p2_taunt = config.getint(_CONF_CONT_P2, _CONF_CONT_TAUNT)
            self.p2_use_joystick = config.getboolean(_CONF_CONT_P2_JS, _CONF_CONT_USE_JS)
            if self.p2_use_joystick:
                self.p2_js_name = config.get(_CONF_CONT_P2_JS, _CONF_CONT_NAME_JS)
                self.p2_js_id = config.getint(_CONF_CONT_P2_JS, _CONF_CONT_ID_JS)
                self.p2_js_left = config.get(_CONF_CONT_P2_JS, _CONF_CONT_LEFT)
                self.p2_js_right = config.get(_CONF_CONT_P2_JS, _CONF_CONT_RIGHT)
                self.p2_js_up = config.get(_CONF_CONT_P2_JS, _CONF_CONT_UP)
                self.p2_js_down = config.get(_CONF_CONT_P2_JS, _CONF_CONT_DOWN)
                self.p2_js_action_l = config.get(_CONF_CONT_P2_JS, _CONF_CONT_AL)
                self.p2_js_action_r = config.get(_CONF_CONT_P2_JS, _CONF_CONT_AR)
                self.p2_js_interact = config.get(_CONF_CONT_P2_JS, _CONF_CONT_INT)
                self.p2_js_taunt = config.get(_CONF_CONT_P2_JS, _CONF_CONT_TAUNT)
                self.p2_js_accept = config.get(_CONF_CONT_P2_JS, _CONF_CONT_ACCEPT_JS)  # ~= Return
                self.p2_js_cancel = config.get(_CONF_CONT_P2_JS, _CONF_CONT_CANCEL_JS)  # ~= ESC
        except (configparser.NoSectionError, configparser.NoOptionError, TypeError, ValueError, AttributeError):
            self.write_settings(True)

    def write_settings(self, default=False):
        """save the current used settings

        Args:
            default (bool): true to save all default values to the disk
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
                self.fullscreen = False
                self.switch_resolution = False
                # default audio settings
                self.play_music = True
                self.vol_music = 10
                self.play_sfx = True
                self.vol_sfx = 10
                # controls for player 1
                self.p1_left = K_LEFT
                self.p1_right = K_RIGHT
                self.p1_up = K_UP
                self.p1_down = K_DOWN
                self.p1_action_l = K_RALT
                self.p1_action_r = K_RSHIFT
                self.p1_interact = K_BACKSPACE
                self.p1_taunt = K_RETURN
                self.p1_use_joystick = False
                # controls for player 2
                self.p2_left = K_a
                self.p2_right = K_d
                self.p2_up = K_w
                self.p2_down = K_s
                self.p2_action_l = K_q
                self.p2_action_r = K_e
                self.p2_interact = K_LSHIFT
                self.p2_taunt = K_TAB
                self.p2_use_joystick = False

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
            '''controls for player 1'''
            try:
                config.add_section(_CONF_CONT_P1)
            except cp_duplicate_section_error:
                pass
            config.set(_CONF_CONT_P1, _CONF_CONT_LEFT, self.p1_left)
            config.set(_CONF_CONT_P1, _CONF_CONT_RIGHT, self.p1_right)
            config.set(_CONF_CONT_P1, _CONF_CONT_UP, self.p1_up)
            config.set(_CONF_CONT_P1, _CONF_CONT_DOWN, self.p1_down)
            config.set(_CONF_CONT_P1, _CONF_CONT_AL, self.p1_action_l)
            config.set(_CONF_CONT_P1, _CONF_CONT_AR, self.p1_action_r)
            config.set(_CONF_CONT_P1, _CONF_CONT_INT, self.p1_interact)
            config.set(_CONF_CONT_P1, _CONF_CONT_TAUNT, self.p1_taunt)
            try:
                config.add_section(_CONF_CONT_P1_JS)
            except cp_duplicate_section_error:
                pass
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_USE_JS, self.p1_use_joystick)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_NAME_JS, self.p1_js_name)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_ID_JS, self.p1_js_id)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_LEFT, self.p1_js_left)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_RIGHT, self.p1_js_right)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_UP, self.p1_js_up)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_DOWN, self.p1_js_down)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_AL, self.p1_js_action_l)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_AR, self.p1_js_action_r)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_INT, self.p1_js_interact)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_TAUNT, self.p1_js_taunt)
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_ACCEPT_JS, self.p1_js_accept)  # ~= Return
            config.set(_CONF_CONT_P1_JS, _CONF_CONT_CANCEL_JS, self.p1_js_cancel)  # ~= ESC

            '''controls for player 2'''
            try:
                config.add_section(_CONF_CONT_P2)
            except cp_duplicate_section_error:
                pass
            config.set(_CONF_CONT_P2, _CONF_CONT_LEFT, self.p2_left)
            config.set(_CONF_CONT_P2, _CONF_CONT_RIGHT, self.p2_right)
            config.set(_CONF_CONT_P2, _CONF_CONT_UP, self.p2_up)
            config.set(_CONF_CONT_P2, _CONF_CONT_DOWN, self.p2_down)
            config.set(_CONF_CONT_P2, _CONF_CONT_AL, self.p2_action_l)
            config.set(_CONF_CONT_P2, _CONF_CONT_AR, self.p2_action_r)
            config.set(_CONF_CONT_P2, _CONF_CONT_INT, self.p2_interact)
            config.set(_CONF_CONT_P2, _CONF_CONT_TAUNT, self.p2_taunt)
            try:
                config.add_section(_CONF_CONT_P2_JS)
            except cp_duplicate_section_error:
                pass
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_USE_JS, self.p2_use_joystick)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_NAME_JS, self.p2_js_name)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_ID_JS, self.p2_js_id)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_LEFT, self.p2_js_left)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_RIGHT, self.p2_js_right)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_UP, self.p2_js_up)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_DOWN, self.p2_js_down)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_AL, self.p2_js_action_l)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_AR, self.p2_js_action_r)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_INT, self.p2_js_interact)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_TAUNT, self.p2_js_taunt)
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_ACCEPT_JS, self.p2_js_accept)  # ~= Return
            config.set(_CONF_CONT_P2_JS, _CONF_CONT_CANCEL_JS, self.p2_js_cancel)  # ~= ESC
            with open(CONFIG, 'w') as configfile:
                config.write(configfile)

        except cp_permission_error:
            print("The config file is locked or not writable.")
            print("Please delete config.cfg or make sure you have write access")

    def setup_joystick(self):
        """get machine readable joystick config format"""

        def parse_config(player, name):
            """change the human readable config strings to dictionaries"""
            if player is 1:
                jid = self.p1_js_id
            else:
                jid = self.p2_js_id
            if "Button" in name:
                # {'button': 1, 'joy': 0}
                return {'button': int(name[7:]), 'joy': jid}
            elif "Hat" in name:
                # {'joy': 0, 'value': (-1, 0), 'hat': 0}
                name = name[4:]
                hid = int(name[:1])
                val = make_tuple(name[2:])
                return {'joy': jid, 'value': val, 'hat': hid}
            elif "Axis" in name:
                # {'axis': 1, 'joy': 0, 'value': -0.1686452833643605}
                name = name[5:]
                axis = int(name[:1])
                val = make_tuple(name[2:])
                return {'value': val, 'axis': axis, 'joy': jid}

        '''stop motion'''
        if self.p1_use_joystick:
            p1_js_left = parse_config(1, self.p1_js_left)
            p1_js_stop = p1_js_left.copy()
            p1_js_stop['value'] = (0, 0)  # centered hats/axis is 0, 0
            self.p1_js_stop = p1_js_stop

            self.p1_key_map = {
                str(parse_config(1, self.p1_js_up)): self.p1_up,
                str(parse_config(1, self.p1_js_down)): self.p1_down,
                str(parse_config(1, self.p1_js_left)): self.p1_left,
                str(parse_config(1, self.p1_js_right)): self.p1_right,
                str(parse_config(1, self.p1_js_action_l)): self.p1_action_l,
                str(parse_config(1, self.p1_js_action_r)): self.p1_action_r,
                str(parse_config(1, self.p1_js_cancel)): K_ESCAPE
            }

            self.p1_menu_map = {
                str(parse_config(1, self.p1_js_up)): K_UP,
                str(parse_config(1, self.p1_js_down)): K_DOWN,
                str(parse_config(1, self.p1_js_left)): K_LEFT,
                str(parse_config(1, self.p1_js_right)): K_RIGHT,
                str(parse_config(1, self.p1_js_accept)): K_RETURN,
                str(parse_config(1, self.p1_js_cancel)): K_ESCAPE
            }

        if self.p2_use_joystick:
            p2_js_left = parse_config(2, self.p2_js_left)
            p2_js_stop = p2_js_left.copy()
            p2_js_stop['value'] = (0, 0)  # centered hats/axis is 0, 0
            self.p2_js_stop = p2_js_stop

            self.p2_key_map = {
                str(parse_config(2, self.p2_js_up)): self.p2_up,
                str(parse_config(2, self.p2_js_down)): self.p2_down,
                str(parse_config(2, self.p2_js_left)): self.p2_left,
                str(parse_config(2, self.p2_js_right)): self.p2_right,
                str(parse_config(2, self.p2_js_action_l)): self.p2_action_l,
                str(parse_config(2, self.p2_js_action_r)): self.p2_action_r,
                str(parse_config(2, self.p2_js_cancel)): K_ESCAPE
            }

            self.p2_menu_map = {
                str(parse_config(2, self.p2_js_up)): K_UP,
                str(parse_config(2, self.p2_js_down)): K_DOWN,
                str(parse_config(2, self.p2_js_left)): K_LEFT,
                str(parse_config(2, self.p2_js_right)): K_RIGHT,
                str(parse_config(2, self.p2_js_accept)): K_RETURN,
                str(parse_config(2, self.p2_js_cancel)): K_ESCAPE
            }
