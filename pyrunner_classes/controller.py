#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division


class Controller(object):

    """player controls manager"""

    def __init__(self, level, config, network_connector):
        self.player_1 = level.player_1
        self.player_2 = level.player_2
        self.network_connector = network_connector
        self.config = config

    def interpret_key(self, key):
        """controls and key settings if the game is in foreground"""
        # TODO move both players
        if self.player_1:
            if key == self.config.p1_left:
                self.player_1.go_left()
            elif key == self.config.p1_right:
                self.player_1.go_right()
            elif key == self.config.p1_up:
                self.player_1.go_up()
            elif key == self.config.p1_down:
                self.player_1.go_down()
            # TODO actions for both players
            elif key == self.config.p1_action_l:
                self.player_1.dig_left()
                print("Player 1 digs left")
            elif key == self.config.p1_action_r:
                self.player_1.dig_right()
                print("Player 1 digs right")
            elif key == self.config.p1_interact:
                print("Player 1 interacts")
            elif key == self.config.p1_taunt:
                print("Player 1 taunts")
            elif key == self.config.p1_jump:
                pass
        if self.player_2:
            # TODO the same for player 2
            if key == self.config.p2_left:
                self.player_2.go_left()
            elif key == self.config.p2_right:
                self.player_2.go_right()
            elif key == self.config.p2_up:
                self.player_2.go_up()
            elif key == self.config.p2_down:
                self.player_2.go_down()
            elif key == self.config.p2_action_l:
                self.player_2.dig_left()
                print("Player 1 digs left")
            elif key == self.config.p2_action_r:
                self.player_2.dig_right()
            elif key == self.config.p2_interact:
                print("Player 2 interacts")
            elif key == self.config.p2_taunt:
                print("Player 2 taunts")
            elif key == self.config.p2_jump:
                pass
        # TODO: get your crap done
        # self.network_connector.client.send_key(self.current_action)

    def release_key(self, key):
        """stop walking"""
        if self.player_1:
            self.player_1.schedule_stop()
        if self.player_2:
            self.player_2.schedule_stop()
