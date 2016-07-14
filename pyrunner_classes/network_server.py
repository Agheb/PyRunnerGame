#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Network Server"""

import threading
import json

from pyrunner_classes import logging, datetime
from pyrunner_classes.network_shared import *

net_log = logging.getLogger("Network")
srvlog = net_log.getChild("Server")


class Server(threading.Thread, MastermindServerTCP):
    """main network server"""

    def __init__(self, ip, port, main, local_only=False):
        self.ip = ip
        self.port = port
        self.main = main
        self.local_only = local_only
        self.known_clients = []
        self.own_client = None
        self.connected = False
        self.sync_interval = 10  # seconds
        self.sync_time = datetime.now()
        self.sprites_removed = []
        threading.Thread.__init__(self, daemon=True)
        MastermindServerTCP.__init__(self, 1, 1, 5.0)

    def callback_client_handle(self, connection_object, data):
        """Initial point of data arrival. Data is received and passed on"""
        srvlog.info("got: '%s'" % str(data))
        json_data = json.loads(data)
        self.interpret_client_data(json_data, connection_object)

    def interpret_client_data(self, data, con_obj):
        """interprets data send from the client to the server"""

        if data['type'] == Message.type_keep_alive:
            srvlog.debug("Got keep Alive")
            return

        if data['type'] == Message.type_key_update:
            srvlog.debug("Got key Update from Client")
            self.send_key(data['data'], self.known_clients.index(con_obj))
            return

        if data['type'] == Message.type_comp_update:
            # sending the pos of the player to all the clients
            srvlog.debug(data['data'])
            self.send_to_all_clients(Message.type_comp_update_set, data['data'])
            return

        if data['type'] == Message.type_init:
            player_id = data['data']['player_id']
            srvlog.debug("Init succ for client {}".format(player_id))
            self.send_to_all_clients(Message.type_init, data['data'])
            return

        if data['type'] == Message.type_gold_removed:
            srvlog.debug("Got gold removed from Client")
            self.sprites_removed.append(data['data'])
            return

        if data['type'] == Message.type_player_killed:
            srvlog.debug("Player {} got killed, telling other clients").format(data['data'])
            self.send_to_all_clients(Message.type_player_killed, data['data'])
            return

    def callback_connect_client(self, connection_object):
        """this methods gets called on initial connect of a client"""
        srvlog.info("New Client Connected %s" % str(connection_object.address))
        # adding ip to client list to generate the playerId
        if connection_object not in self.known_clients:
            srvlog.debug("Added client to known clients")
            self.known_clients.append(connection_object)
        # sending initial Data, to all clients so everyone is on the same page. TODO:  add info about enemies
        level_info = self.main.level.get_level_info_json()
        # the clients id
        misc_info = {'player_id': str(self.known_clients.index(connection_object)),
                     Message.field_removed_sprites: self.sprites_removed}
        # concat the data
        combined = {}
        for d in (level_info, misc_info):
            combined.update(d)

        data = json.dumps({'type': 'init', 'data': combined})

        self.callback_client_send(connection_object, data)

        # let the others know that there is a new client

        for client in self.known_clients:
            if client != connection_object:
                self.callback_client_send(client, data)

        '''get the up to date player positions'''
        self.send_to_all_clients(Message.type_comp_update)

        '''and up to date bot positions'''
        for bot in self.main.level.bots:
            '''update the bot positions only on the clients'''
            player_info = self.main.level.get_normalized_pos_and_data(bot, True)
            srvlog.debug("sending bot data: ", player_info)
            data = {'player_info':player_info, 'block_info':[]}
            self.send_to_all_clients_except_self(Message.type_comp_update_set, data)

        return super(MastermindServerTCP, self).callback_connect_client(connection_object)

    def callback_disconnect_client(self, connection_object):
        """gets called if a client disconnects"""
        disconnected_client = self.known_clients.index(connection_object)
        srvlog.info("Client disconnected, sending to other clients %s" % disconnected_client)

        # kill the player of the disconnected client on all other clients
        self.send_to_all_clients(Message.type_client_dc, {'client_id': disconnected_client})
        self.known_clients.pop(disconnected_client)
        super(MastermindServerTCP, self).callback_disconnect_client(connection_object)
        return self.send_to_all_clients(Message.type_comp_update)

    def send_key(self, key, player_id):
        """puts a passed key inside a json object and sends it to all clients"""
        srvlog.info("Sending key {} to Client with id {}".format(str(key), str(player_id)))
        self.send_to_all_clients(Message.type_key_update, {'key': str(key), 'player_id': str(player_id)})

    def send_bot_movement(self, action, bot_id):
        """puts a passed key inside a json object and sends it to all clients"""
        srvlog.info("Sending key {} to Client with id {}".format(str(action), str(bot_id)))
        self.send_to_all_clients(Message.type_bot_update, {'key': str(action), 'bot_id': str(bot_id)})

    def notify_level_changed(self, level):
        """notify all clients when level sprites changed"""
        self.send_to_all_clients_except_self(Message.type_level_changed, {Message.field_level_name: level})

    def send_to_all_clients(self, message, data=None):
        """send message to all clients"""
        json_data = json.dumps({'type': message, 'data': data})
        for client in self.known_clients:
            self.callback_client_send(client, json_data)

    def send_to_all_clients_except_self(self, message, data=None):
        """send information to all clients except yourself"""
        json_data = json.dumps({'type': message, 'data': data})
        for index, client in enumerate(self.known_clients):
            if index != self.own_client:
                self.callback_client_send(client, json_data)

    def kill(self):
        """kill this server thread"""
        try:
            self.accepting_disallow()
        except AttributeError:
            pass
        try:
            self.disconnect_clients()
        except AttributeError:
            pass
        try:
            self.disconnect()
        except AttributeError:
            pass

    def run(self):
        """keep the server running"""
        try:
            self.connect(self.ip, self.port)
            self.accepting_allow()
            self.connected = True
        except (OSError, MastermindErrorSocket):
            srvlog.info(str(OSError))
            srvlog.info(str(MastermindErrorSocket))
            pass
            # self.port = self.port + 1 if self.port and self.port < START_PORT else START_PORT
        srvlog.info("server started and accepting connections on port %s" % self.port)

    def callback_disconnect(self):
        """let clients know when the server disconnected"""
        srvlog.info("Server disconnected from network")
        return super(MastermindServerTCP, self).callback_disconnect()

    def update(self):
        """update all clients"""
        pass
        # if len(self.known_clients) > 1:
        #     if (datetime.now() - self.sync_time).seconds >= self.sync_interval:
        #         '''sync all players every x seconds'''
        #         srvlog.info("sending update data to clients")
        #         for bot in self.level.bots:
        #             '''update the bot positions only on the clients'''
        #             player_info = self.level.get_normalized_pos_and_data(bot, True)
        #             srvlog.debug("sending bot data: ", player_info)
        #             self.send_to_all_clients_except_self(Message.type_comp_update_set, player_info)
        #         self.send_to_all_clients(Message.type_comp_update)
        #         self.sync_time = datetime.now()

    def send_bot_pos_and_data(self, bot):
        """send updated bot movements to all clients"""
        player_info = self.main.level.get_normalized_pos_and_data(bot, True)
        srvlog.debug("sending bot data: ", player_info)
        data = {'player_info':player_info, 'block_info':[]}
        self.send_to_all_clients_except_self(Message.type_comp_update_set, data)

    def get_collected_data(self):
        """gather collected data"""
        collected_data = {}
        collected_data[Message.field_player_locations] = self.main.level.get_player_data()
        return collected_data

    @property
    def level(self):
        """return the current level"""
        return self._level

    @level.setter
    def level(self, level):
        """set the current level"""
        self._level = level
        for client_id in range(len(self.known_clients)):
            self.main.level.add_player(client_id)
