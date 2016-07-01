#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
import threading
import logging
from pprint import pprint
import pdb

import Mastermind
from .controller import Controller
from datetime import datetime
import json
from Mastermind import *

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parentdir)
netlog = logging.getLogger("Network")
srvlog = netlog.getChild("Server")
clientlog = netlog.getChild("Client")

START_PORT = 6799


class NetworkConnector(object):
    """the main network class"""

    COMPRESSION = None

    def __init__(self, main, level):
        self.ip = "localhost"
        self.main = main
        self.level = level
        self.port = 6799
        self.client = None
        self.server = None

    def start_server_prompt(self):
        """starting the network server"""

        def start_server():
            """try to start a server"""
            try:
                if not self.server:
                    self.server = Server(self.port, self.level, self.main)
                    self.master = True
                    self.server.start()
                else:
                    self.main.load_level(self.main.START_LEVEL)
            except (OSError, Mastermind._mm_errors.MastermindErrorSocket):
                print(str(self.port))
                self.server.kill()
                self.server = None
                self.port = self.port + 1 if self.port < START_PORT + 10 else START_PORT
                self.start_server_prompt()

        start_server()
        self.join_server_prompt()

    def join_server_prompt(self):

        def join_server():
            try:
                #self.ip = input("Please enter an ip to connect to: ")
                self.client = Client("localhost", self.port, self.level, self.main)
                self.master = False
                self.client.start()
            except (OSError, ConnectionRefusedError, Mastermind._mm_errors.MastermindErrorSocket):
                print(str(self.port))
                self.client.kill()
                self.client = None
                self.port = self.port + 1 if self.port < START_PORT + 10 else START_PORT
                self.join_server_prompt()

        join_server()

    def update(self):
        try:
            self.client.update()
        except (MastermindErrorClient, AttributeError):
            pass


class Client(threading.Thread, MastermindClientTCP):

    """the network client"""
    def __init__(self, ip, port, level, main):
        self.port = port
        self.level = level
        self.target_ip = ip
        self.main = main
        threading.Thread.__init__(self, daemon=True)
        MastermindClientTCP.__init__(self)
        self.timer = datetime.now()  # timer for the keep Alive
        self.player_id = 0
        self.connected = False

    def send_key(self, key):
        clientlog.info("Sending key Action %s to server" % key)
        data = json.dumps({'type': 'key_update', 'data': str(key)})
        self.send(data, compression=NetworkConnector.COMPRESSION)

    def run(self):
        clientlog.info("Connecting to ip %s" % str(self.target_ip))
        self.connect(self.target_ip, self.port)
        clientlog.info("Client connecting, waiting for initData")
        self.connected = True
        self.wait_for_init_data()

    def get_last_command(self):
        # for now, maybe we need non blocking later
        raw_data = self.receive(True)
        data = json.loads(raw_data)
        clientlog.info("Got data from server: {}".format(str(data)))
        if data['type'] == 'key_update':
            clientlog.info("got key_update from server")
            return data['data'], data['player_id']

    def wait_for_init_data(self):
        """start the server and wait for players to connect"""
        init_data_raw = self.receive(True)
        data = json.loads(init_data_raw)
        if data['type'] == 'init':
            clientlog.info("Client got init Data, creating new Player") 
            contents = data['data']
            self.player_id = contents['player_id']

            for pl_center in contents['players']:
                try:
                    pid = int(pl_center.index('player_id'))
                except ValueError:
                    pid = len(self.level.players)
                # add the others
                self.level.add_player(pid, pl_center)
            # add ourself
            self.level.add_player(self.player_id)

            # tell the server that the client is init
            self.send_init_success()
            self.main.menu.show_menu(False)
        else:
            raise Exception('Did not get init as first Package') 

    def send_init_success(self):
        """let the server know the connection succeeded"""
        data = json.dumps({'type': 'init_succ', 'player_id': self.player_id})
        self.send(data, compression=NetworkConnector.COMPRESSION)

    def kill(self):
        """stop the server"""
        self.disconnect()
        self.connected = False

    def update(self):
        """run the server"""
        self.send_keep_alive()
        raw_data = self.receive(False)

        if raw_data:
            data = json.loads(raw_data)
            clientlog.info("Got data from server: {}".format(str(data)))
            if data['type'] == 'key_update':
                clientlog.info("got key_update from server")
                Controller.do_action(data['data'], data['player_id'])
            if data['type'] == 'init_succ':
                clientlog.info("got init succ")
                try:
                    self.level.players[int(data['player_id'])]
                except IndexError:
                    pid = len(self.level.players)
                    self.level.add_player(pid)
                self.main.menu.show_menu(False)

    def send_keep_alive(self):
        """send keep alive if last was x seconds ago"""
        if (datetime.now() - self.timer).seconds > 4:
            data = json.dumps({'type': 'keep_alive'})
            self.send(data, compression=NetworkConnector.COMPRESSION)
            self.timer = datetime.now()
        pass


class Server(threading.Thread, MastermindServerTCP):

    """main network server"""
    def __init__(self, port, level, main):
        self.port = port
        self._level = level
        self.main = main
        self.known_clients = []
        threading.Thread.__init__(self, daemon=True)
        MastermindServerTCP.__init__(self)

    def callback_client_handle(self, connection_object, data):
        """Initial point of data arrival. Data is received and passed on"""
        srvlog.info("got: '%s'" %str(data))
        json_data = json.loads(data)
        self.interpret_client_data(json_data, connection_object)

    def interpret_client_data(self, data, con_obj):
        """interprets data send from the client to the server"""
        if data['type'] == "keep_alive":
            srvlog.debug("Got keep Alive")
            pass
        if data['type'] == "key_update":
            srvlog.debug("Got key Update from Client")
            self.send_key(data['data'], self.known_clients.index(con_obj))
        if data['type'] == "complete_update":
            srvlog.debug("Got full update from Client")
            pass
        if data['type'] == "init_succ":
            player_id = data['player_id']
            srvlog.debug("Init succ for client {}".format(player_id))
            for client in self.known_clients:
                self.callback_client_send(client,json.dumps(data))
            pass

    def callback_connect_client(self, connection_object):
        """this methods gets called on initial connect of a client"""
        srvlog.info("New Client Connected %s" %str(connection_object.address))
        #adding ip to client list to generate the playerId
        if connection_object not in self.known_clients:
            srvlog.debug("Added client to known clients")
            self.known_clients.append(connection_object)
        #sending initial Data, to all clients so everyone is on the same page. TODO:  add info about enemies
        level_info = self.level.get_level_info_json()
        #the clients id
        misc_info = {'player_id': str(self.known_clients.index(connection_object))}
        #concat the data
        combined = {}
        for d in (level_info, misc_info):
            combined.update(d)
        
        data = json.dumps({'type': 'init','data': combined})

        self.callback_client_send(connection_object, data)


        #let the others know that there is a new client

        for client in self.known_clients:
            if client != connection_object:
                self.callback_client_send(client, data)
        
        return super(MastermindServerTCP, self).callback_connect_client(connection_object)

    def send_key(self, key, player_id):
        """puts a passed key inside a json object and sends it to all clients"""
        srvlog.info("Sending key {} to Client with id {}".format(str(key), str(player_id)))
        data = json.dumps({'type': 'key_update', 'data': str(key), 'player_id': str(player_id)})
        for client in self.known_clients:
            self.callback_client_send(client, data)

    def kill(self):
        self.accepting_disallow()
        self.disconnect_clients()
        self.disconnect()

    def run(self):
        self.connect("localhost", self.port)
        self.accepting_allow()
        srvlog.info("server started and accepting connections on port %s" % self.port)

    def callback_disconnect(self):
        srvlog.info("Server disconnected from network")
        return super(MastermindServerTCP, self).callback_disconnect()

    @property
    def level(self):
        """return the current level"""
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

        for client_id in range(len(self.known_clients)):
            self.level.add_player(client_id)

        # TODO
        # re-add players for each client on level change
