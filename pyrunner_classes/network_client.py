#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Network Client"""
# Python 2 related fixes
from __future__ import division

import pdb
import threading
import json

from pyrunner_classes import logging, datetime, Controller, WorldObject
from pyrunner_classes.network_shared import *

net_log = logging.getLogger("Network")
client_log = net_log.getChild("Client")


class Client(threading.Thread, MastermindClientTCP):
    """the network client"""

    def __init__(self, ip, port, main, master):
        self.port = port
        self.target_ip = ip
        self.main = main
        self.master = master
        threading.Thread.__init__(self, daemon=True)
        MastermindClientTCP.__init__(self)
        self.timer = datetime.now()  # timer for the keep Alive
        self.player_id = None
        self.connected = False

    def send_key(self, key):
        """send the current pressed key action"""
        client_log.info("Sending key Action %s to server" % key)
        data = json.dumps({'type': 'key_update', 'data': str(key)})
        self.send(data, compression=COMPRESSION)

    def run(self):
        """keep the server running"""
        client_log.info("Connecting to ip %s" % str(self.target_ip))
        try:
            self.connect(self.target_ip, self.port)
            client_log.info("Client connecting, waiting for initData")
            self.connected = True
            self.wait_for_init_data()
        except (OSError, MastermindErrorSocket, MastermindErrorClient):
            error = "An error occurred connecting to the server."
            error += " %s:%s Please try again later." % (self.target_ip, self.port)
            self.main.menu.network.print_error(error)
            pass
            # self.port = self.port + 1 if self.port and self.port < START_PORT else START_PORT

    def wait_for_init_data(self):
        """start the server and wait for players to connect"""
        init_data_raw = self.receive(True)
        data = json.loads(init_data_raw)
        if data['type'] == 'init':
            client_log.info("Client got init Data, creating new Player")
            contents = data['data']
            self.player_id = int(contents['player_id'])
            if self.master:
                self.main.network_connector.server.own_client = self.player_id

            for pl_center in contents['players']:
                try:
                    pid = int(pl_center.index('player_id'))
                except ValueError:
                    pid = len(self.main.level.players)
                # add the others
                self.main.level.add_player(pid, pl_center)
            # add ourself
            self.main.level.add_player(self.player_id)

            # kill removed sprites_removed
            removed_sprite_ids_list = contents[Message.field_removed_sprites]
            tupeld = []
            for a in removed_sprite_ids_list:
                tupeld.append((a[0], a[1]))

            self.main.level.physics.remove_sprites_by_id(tupeld)

            # tell the server that the client is init
            self.send_init_success()
            self.main.menu.show_menu(False)
        else:
            raise Exception('Did not get init as first Package')

    def gold_removed(self, index):
        """sync removed gold"""
        client_log.info("Gold removed, notifying server")
        self.send_data_to_server(Message.type_gold_removed, index)

    def player_killed(self):
        """sync player deaths"""
        client_log.info("Player got killed sending to server")
        self.send_data_to_server(Message.type_player_killed, self.player_id)

    def send_init_success(self):
        """let the server know the connection succeeded"""
        data = {'player_id': self.player_id}
        self.send_data_to_server(Message.type_init, data)

    def send_data_to_server(self, message_type, py_data):
        """send data from the client back to the server"""
        data = json.dumps({'type': message_type, 'data': py_data})
        self.send(data, compression=COMPRESSION)

    def kill(self):
        """stop the server"""
        try:
            self.disconnect()
        except AttributeError:
            pass
        self.connected = False

    def update(self):
        """run the server"""
        self.send_keep_alive()
        raw_data = self.receive(False)

        if raw_data:
            data = json.loads(raw_data)
            client_log.info("Got data from server: {}".format(str(data)))
            if data['type'] == Message.type_key_update:
                client_log.info("got key_update from server")
                Controller.do_action(data['data']['key'], data['data']['player_id'])
                return

            if data['type'] == Message.type_bot_update:
                client_log.info("got bot_update from server")
                Controller.bot_action(data['data']['key'], data['data']['bot_id'])
                return

            if data['type'] == Message.type_init:
                client_log.info("got init succ")
                try:
                    self.main.level.players[int(data['data']['player_id'])]
                except IndexError:
                    pid = len(self.main.level.players)
                    self.main.level.add_player(pid)
                self.main.menu.show_menu(False)
                return

            if data['type'] == Message.type_client_dc:
                client_log.info("A client disconnected, removing from game")
                pid = data['data']['client_id']
                if not self.main.level.remove_player(pid):
                    client_log.error("Could not remove player form player list!")
                else:
                    client_log.info("removed player form playerlist")
                return

            if data['type'] == Message.type_comp_update:
                client_log.info("Sending own Pos to Server")
                self.send_current_pos_and_data()
                return

            if data['type'] == Message.type_comp_update_states:
                client_log.info("Sending own states to Server")
                player = self.main.level.players[self.player_id]
                player_info = self.main.level.get_normalized_pos_and_data(player, False, False)
                self.send_data_to_server(Message.type_comp_update, player_info)
                return

            if data['type'] == Message.type_level_changed:
                client_log.info("Got change level from Server")
                level_name = data[Message.field_level_name]
                self.main.level.load_level(level_name)
                return

            if data['type'] == Message.type_comp_update_set:
                '''don't set the positions on the server'''
                player_id, normalized_pos, is_bot, info = data['data']
                player_id = int(player_id)
                is_bot = bool(int(is_bot))

                if is_bot or player_id != self.player_id:
                    client_log.debug("received player data: ", data['data'])
                    client_log.info("Got pos setter from server")
                    client_log.debug("setting player data: ", data['data'])
                    self.main.level.set_player_data(player_id, normalized_pos, is_bot, info)
                return

            if data['type'] == Message.type_gold_removed:
                # Todo maybe remove gold if the sync is not working
                client_log.info("Gold removed received from server, killing gold")
                WorldObject.kill_world_object(data['data'])
                return

            if data['type'] == Message.type_player_killed:
                client_log.info("Got player killed from Server")
                pdb.set_trace()
                for player in self.main.level.players:
                    if player.player_id == data['data']:
                        player.kill()

    def send_current_pos_and_data(self):
        """send the current position and state vars to the server"""
        try:
            player = self.main.level.players[self.player_id]
            player_info = self.main.level.get_normalized_pos_and_data(player, False)
            self.send_data_to_server(Message.type_comp_update, player_info)
        except IndexError:
            pass

    def send_keep_alive(self):
        """send keep alive if last was x seconds ago"""
        if (datetime.now() - self.timer).seconds > 4 and self.connected:
            data = json.dumps({'type': Message.type_keep_alive})
            try:
                self.send(data, compression=COMPRESSION)
            except MastermindErrorClient:
                self.main.menu.network.print_error("An error occurred while trying to send data to the server.")
            self.timer = datetime.now()
        pass
