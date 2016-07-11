#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main package handling all important game classes"""
# game framework
import pygame
# often used classes
import logging
from datetime import datetime
# basic game structure
from .constants import *
from .main_config import MainConfig
from .menu import Menu, MenuItem
from .main_menu import MainMenu
from .render_thread import RenderThread
from .sound_thread import MusicMixer
# World
from .level import Level
from .level_objecs import WorldObject, Rope, Ladder, Collectible, ExitGate
from .game_physics import Physics
# Players
from .spritesheet_handling import SpriteSheet
from .player import Player
from .player_objects import GoldScore
from .non_player_characters import Bots
from .dijkstra import Graph
from .npc_state_machine import StateMachine
from .npc_states import Exploring, Hunting, ShortestPath
# Network
from .controller import Controller
from .network_connector import NetworkConnector
from .network_client import Client
from .network_server import Server
from .network_shared import Action, Message, COMPRESSION
from .zeroconf_bonjour import ZeroConfAdvertiser, ZeroConfListener


__all__ = ['pygame', 'datetime', 'logging',
           'BLUE', 'YELLOW', 'RED', 'BLACK', 'BACKGROUND', 'GRAY', 'WHITE', 'MENU_FONT',
           'MainConfig', 'Menu', 'MenuItem', 'MainMenu', 'RenderThread', 'MusicMixer',
           'NetworkConnector', 'Client', 'Server', 'Controller', 'Action', 'Message',
           'COMPRESSION', 'ZeroConfAdvertiser', 'ZeroConfListener',
           'SpriteSheet', 'Player', 'GoldScore',
           'Bots', 'Graph', 'StateMachine', 'Exploring', 'ShortestPath', 'Hunting',
           'Level', 'Physics', 'WorldObject', 'ExitGate', 'Ladder', 'Rope', 'Collectible']

__version__ = '0.1.5'
__author__ = 'Team pyBerries'
__description__ = 'Sub Classes of the pyRunner Game'
