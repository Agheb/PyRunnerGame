#!/usr/bin/python
# -*- coding: utf-8 -*-
"""main pyRunner class which initializes all sub classes and threads"""
# Python 2 related fixes
from __future__ import division
import pdb
from .game_physics import Physics 
class Action():
    LEFT = "go_left"
    RIGHT = "go_right"
    UP = "go_up"
    DOWN = "go_down"
    DIG_LEFT = "dig_left"
    DIG_RIGHT = "dig_right"

class Controller():

    """player controls manager"""
    def __init__(self, config, network_connector):
        self.network_connector = network_connector
        # self.player2 = player2
        self.config = config

    def interpret_key(self, key):
        """controls and key settings if the game is in foreground"""
        # TODO move both players
        if key == self.config.p1_left:
            self.current_action = Action.LEFT
        elif key == self.config.p1_right:
            self.current_action = Action.RIGHT
        elif key == self.config.p1_up:
            self.current_action = Action.UP
        elif key == self.config.p1_down:
            self.current_action = Action.DOWN
        # TODO actions for both players
        elif key == self.config.p1_action_l:
            self.player1.dig_left()
            print("Player 1 digs left")
        elif key == self.config.p1_action_r:
            self.player1.dig_right()
            print("Player 1 digs right")
        elif key == self.config.p1_interact:
            print("Player 1 interacts")
        elif key == self.config.p1_taunt:
            print("Player 1 taunts")
        elif key == self.config.p1_jump:
            pass
        # TODO the same for player 2
        elif key == self.config.p2_left:
            print("Player 2 moves left")
        elif key == self.config.p2_right:
            print("Player 2 moves right")
        elif key == self.config.p2_up:
            print("Player 2 moves up")
        elif key == self.config.p2_down:
            print("Player 2 moves down")
        # TODO actions for both players
        elif key == self.config.p2_action_l:
            print("Player 2 digs left")
        elif key == self.config.p2_action_r:
            print("Player 2 digs right")
        elif key == self.config.p2_interact:
            print("Player 2 interacts")
        elif key == self.config.p2_taunt:
            print("Player 2 taunts")
        
        self.network_connector.client.send_key(self.current_action)
        #command, playerNum = self.network_connector.client.get_last_command()
        #self.do_action(command, playerNum)

    def release_key(self, key):
        """stop walking"""
        for p in Physics.players:
            p.schedule_stop()

    @staticmethod
    def do_action(action, playerNum):
        playerNum = int(playerNum)
        pdb.set_trace()
        if action == Action.LEFT:
            Physics.players[playerNum].go_left()
        elif action == Action.RIGHT:
            Physics.players[playerNum].go_right()
        elif action == Action.UP:
            Physics.players[playerNum].go_up()
