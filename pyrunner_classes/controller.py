#!/usr/bin/python
# -*- coding: utf-8 -*-
"""controller class that translates key presses into actions (and vice versa) and sends them to the server"""
from pyrunner_classes.network_shared import *
from pyrunner_classes.level import Level


class Controller(object):

    """player controls manager"""

    def __init__(self, config, network_connector):
        """initialize the controller class"""
        '''
        self.player_1 = level.player_1
        self.player_2 = level.player_2
        '''
        self.config = config
        self.network_connector = network_connector
        self.player_1_movements = []
        self.player_2_movements = []
        '''only stop player if movement key got released'''
        self.player_1_movements.append(self.config.p1_left)
        self.player_1_movements.append(self.config.p1_right)
        self.player_1_movements.append(self.config.p1_up)
        self.player_1_movements.append(self.config.p1_down)
        self.player_2_movements.append(self.config.p2_left)
        self.player_2_movements.append(self.config.p2_right)
        self.player_2_movements.append(self.config.p2_up)
        self.player_2_movements.append(self.config.p2_down)

    def interpret_key(self, key):
        """controls and key settings if the game is in foreground"""
        current_action = None

        # TODO move both players
        if key == self.config.p1_left:
            current_action = Action.LEFT
        elif key == self.config.p1_right:
            current_action = Action.RIGHT
        elif key == self.config.p1_up:
            current_action = Action.UP
        elif key == self.config.p1_down:
            current_action = Action.DOWN
        elif key == self.config.p1_action_l:
            current_action = Action.DIG_LEFT
        elif key == self.config.p1_action_r:
            current_action = Action.DIG_RIGHT
        elif key == self.config.p1_interact:
            print("Player 1 interacts")
        elif key == self.config.p1_taunt:
            print("Player 1 taunts")
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

        if current_action:
            try:
                self.network_connector.client.send_key(current_action)
            except MastermindErrorClient:
                for player in Level.players:
                    player.kill()
            # command, playerNum = self.network_connector.client.get_last_command()
            # self.do_action(self.current_action, 0)

    def release_key(self, key=None):
        """stop walking"""
        '''
        if self.player_1 and key in self.player_1_movements:
            self.player_1.stop_on_ground = True
        if self.player_2 and key in self.player_2_movements:
            self.player_2.stop_on_ground = True
        '''
        try:
            # if player.pid == 0 and key in self.player_1_movements:
            if key in self.player_1_movements or self.player_2_movements:
                self.network_connector.client.send_key(Action.STOP)
        except MastermindErrorClient:
            for player in Level.players:
                player.kill()
        # self.do_action(Action.STOP, 0)

    @staticmethod
    def do_action(action, player_num):
        """perform an action for each player"""
        player_num = int(player_num)

        if player_num < len(Level.players):
            if action == Action.LEFT:
                Level.players[player_num].go_left()
            elif action == Action.RIGHT:
                Level.players[player_num].go_right()
            elif action == Action.UP:
                Level.players[player_num].go_up()
            elif action == Action.DOWN:
                Level.players[player_num].go_down()
            elif action == Action.DIG_LEFT:
                Level.players[player_num].dig_left()
            elif action == Action.DIG_RIGHT:
                Level.players[player_num].dig_right()
            elif action == Action.STOP:
                Level.players[player_num].stop_on_ground = True

    @staticmethod
    def bot_action(action, bot_num):
        """perform an action for each player"""
        bot_num = int(bot_num)

        if bot_num < len(Level.bots):
            if action == Action.LEFT:
                Level.bots[bot_num].move_left()
            elif action == Action.RIGHT:
                Level.bots[bot_num].move_right()
            elif action == Action.UP:
                Level.bots[bot_num].move_up()
            elif action == Action.DOWN:
                Level.bots[bot_num].move_down()
            elif action == Action.STOP:
                Level.bots[bot_num].stop_on_ground = True
