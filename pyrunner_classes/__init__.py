#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main package handling all important game classes"""
from .constants import *
from .main_config import MainConfig
from .menu import Menu, MenuItem
from .main_menu import MainMenu
from .render_thread import RenderThread
from .sound_thread import MusicMixer
from .level import Level
from .level_objecs import *
from .player import Player
from .player_objects import GoldScore
from .game_physics import Physics
from .controller import Controller
from .network_connector import NetworkConnector

__all__ = ['BLUE', 'YELLOW', 'RED', 'BLACK', 'BACKGROUND', 'GRAY', 'WHITE',
           'MainConfig', 'Menu', 'MenuItem', 'MainMenu', 'RenderThread', 'MusicMixer',
           'Level', 'Physics', 'Controller', 'NetworkConnector',
           'Player', 'GoldScore', 'WorldObject', 'ExitGate']


__version__ = '0.1.3'
__author__ = 'Team pyBerries'
__description__ = 'Sub Classes of the pyRunner Game'
