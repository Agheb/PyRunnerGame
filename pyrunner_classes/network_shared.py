#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Shared Network Objects/Constants"""

from libs.Mastermind import *

COMPRESSION = None


class Action(object):
    """store all available actions"""
    LEFT = "go_left"
    RIGHT = "go_right"
    UP = "go_up"
    DOWN = "go_down"
    STOP = "stop"
    DIG_LEFT = "dig_left"
    DIG_RIGHT = "dig_right"


class Message(object):
    """just a wrapper object to store messages in one place"""

    '''types'''
    type_client_dc = "client_disconnected"
    type_key_update = "key_update"
    type_bot_update = "bot_update"
    type_init = 'init_succ'
    type_comp_update = 'update_all'
    type_comp_update_states = 'update_states'
    type_comp_update_set = 'update_all_set'
    type_keep_alive = 'keep_alive'
    type_level_changed = 'level_changed'
    type_gold_removed = 'gold_removed'
    type_player_killed = 'player_killed'

    '''data fields'''
    field_player_locations = "player_locations"
    field_level_name = "level_name"
    field_removed_sprites = "removed_sprites"
