#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main package handling all important game classes"""
from .constants import *
from .main_config import MainConfig
from .menu import Menu, MenuItem
from .main_menu import MainMenu
from .render_thread import RenderThread
from .sound_thread import MusicMixer
from .levels import Level, Level_01, Level_02
from .platforms import MovingPlatform, Platform
from .spritesheet_functions import SpriteSheet
from .player import Player

__all__ = ['BLUE', 'YELLOW', 'RED', 'BLACK', 'BACKGROUND', 'GRAY', 'WHITE',
           'MainConfig', 'Menu', 'MenuItem', 'MainMenu', 'RenderThread', 'MusicMixer']

__version__ = '0.1.3'
__author__ = 'Team pyBerries'
__description__ = 'Sub Classes of the pyRunner Game'
