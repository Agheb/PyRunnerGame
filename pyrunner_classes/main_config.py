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
_CONF_CONT_LEFT = "left"
_CONF_CONT_RIGHT = "right"
_CONF_CONT_UP = "up"
_CONF_CONT_DOWN = "down"
_CONF_CONT_AL = "action left"
_CONF_CONT_AR = "action right"
_CONF_CONT_INT = "interact"
_CONF_CONT_TAUNT = "taunt"
_CONF_CONT_JUMP = "jump"


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
        '''read the configuration file to initialize above variables'''
        self.config_parser = self.init_config_parser()
        self.read_settings()

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
            '''controls for player 2'''
            self.p2_left = config.getint(_CONF_CONT_P2, _CONF_CONT_LEFT)
            self.p2_right = config.getint(_CONF_CONT_P2, _CONF_CONT_RIGHT)
            self.p2_up = config.getint(_CONF_CONT_P2, _CONF_CONT_UP)
            self.p2_down = config.getint(_CONF_CONT_P2, _CONF_CONT_DOWN)
            self.p2_action_l = config.getint(_CONF_CONT_P2, _CONF_CONT_AL)
            self.p2_action_r = config.getint(_CONF_CONT_P2, _CONF_CONT_AR)
            self.p2_interact = config.getint(_CONF_CONT_P2, _CONF_CONT_INT)
            self.p2_taunt = config.getint(_CONF_CONT_P2, _CONF_CONT_TAUNT)
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
                self.fullscreen = True
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
                self.p1_jump = K_SPACE
                # controls for player 2
                self.p2_left = K_a
                self.p2_right = K_d
                self.p2_up = K_w
                self.p2_down = K_s
                self.p2_action_l = K_q
                self.p2_action_r = K_e
                self.p2_interact = K_LSHIFT
                self.p2_taunt = K_TAB
                self.p2_jump = K_LSUPER

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

            with open(CONFIG, 'w') as configfile:
                config.write(configfile)

        except cp_permission_error:
            print("The config file is locked or not writable.")
            print("Please delete config.cfg or make sure you have write access")
