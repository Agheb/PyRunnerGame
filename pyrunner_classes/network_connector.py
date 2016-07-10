#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
import threading
import logging
import json
import socket
from .player import Player
from .controller import Controller
from datetime import datetime
from time import sleep
from libs.Mastermind import *
from .level_objecs import WorldObject
from .zeroconf_bonjour import ZeroConfAdvertiser, ZeroConfListener

netlog = logging.getLogger("Network")
srvlog = netlog.getChild("Server")
clientlog = netlog.getChild("Client")

START_PORT = 6799


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


class NetworkConnector(object):
    """the main network class"""

    COMPRESSION = None

    def __init__(self, main, level):
        self.ip = "0.0.0.0"
        socket_ip = socket.gethostbyname(socket.gethostname())
        network_ip = self.get_network_ip()
        self.external_ip = socket_ip
        self.main = main
        self.level = level
        self.port = START_PORT
        self.master = False
        self.client = None
        self.server = None
        self.browser = None
        self.advertiser = None
        self.register_physics_callback()

        '''get IP'''
        if socket_ip.startswith("127."):
            if not network_ip.startswith("127."):
                self.external_ip = network_ip
            else:
                try:
                    self.external_ip = socket.gethostbyname(socket.getfqdn())
                except OSError:
                    try:
                        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        s.connect(('8.8.8.8', 0))
                        self.external_ip = s.getsockname()[0]
                    except OSError:
                        self.external_ip = "0.0.0.0"


    @staticmethod
    def get_network_ip():
        """get the local ip"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.connect(('<broadcast>', 0))
            return s.getsockname()[0]

        except OSError:
            return "127.0.0.1"

    def quit(self):
        """shutdown all threads"""
        try:
            self.server.kill()
            self.client.kill()
            self.browser.kill()
            self.advertiser.shutdown()
        except AttributeError:
            pass

    def init_new_server(self, local_only=False):
        """start a new server thread"""
        if self.server:
            self.server.kill()

        self.server = Server(self.ip, self.port, self.level, self.main, local_only)
        self.master = True
        self.server.start()

    def register_physics_callback(self):
        #adds the network connector to the physics
        self.level.physics.register_callback(self)

    def start_local_game(self):
        """run a single player game"""
        self.start_server_prompt(START_PORT - 10, True)

    def start_server_prompt(self, port=START_PORT, local_only=False):
        """starting a network server from the main menu"""
        self.ip = "0.0.0.0" if not local_only else "127.0.0.1"
        self.port = port if port else START_PORT

        def start_server():
            """try to start a server"""

            if not self.server:

                self.init_new_server(local_only)

                while not self.server.connected:
                    '''give the thread 0.25 seconds to start (warning: this locks the main process)'''
                    sleep(0.25)

                    if not self.server.connected:
                        '''if it fails (e.g. port still in use) switch the port up to 5 times'''
                        if self.port < START_PORT + 5:
                            self.port += 1
                            self.init_new_server()
                            netlog.info("changing server and port to ", str(self.port))
                        else:
                            '''if it still fails give up'''
                            self.server.kill()
                            break
            else:
                if local_only:
                    self.server.kill()
                self.join_server_prompt((self.ip, self.port))
                # self.main.load_level(self.main.START_LEVEL)

        '''starting server'''
        start_server()

        if self.server and self.server.connected:
            self.join_server_prompt((self.ip, self.port))
            '''give the bots their brain'''
            for bot in Player.bots:
                bot.master = True
                bot.network_connector = self
            if not local_only:
                '''propagate server over zeroconf'''
                self.advertiser = ZeroConfAdvertiser(self.external_ip, self.port)

    def join_server_menu(self):
        """browse for games and then join"""
        self.browser = ZeroConfListener(self.main.menu, self, self.ip, self.port)
        self.browser.start()
        self.browser.start_browser()

    def join_server_prompt(self, ip_and_port):
        """join a server from the main menu"""
        ip, self.port = ip_and_port

        if isinstance(ip, str):
            '''let the computer resolve the hostname to an ip'''
            ip = socket.gethostbyname(ip)
        '''change to localhost ip if we are on the same computer'''
        self.ip = ip    # "127.0.0.1" if self.ip == self.external_ip else ip

        '''start a new client thread'''
        if self.client and self.client.connected:
            '''disconnect from other servers first'''
            self.client.disconnect()

        self.client = Client(self.ip, self.port, self.level, self.main, self.master)
        self.client.start()

        if self.client and self.client.connected:
            netlog.info("connected to %s" % self.ip)

    def update(self):
        try:
            self.client.update()
            self.server.update()
        except (MastermindErrorClient, AttributeError):
            pass


class Client(threading.Thread, MastermindClientTCP):

    """the network client"""
    def __init__(self, ip, port, level, main, master):
        self.port = port
        self.level = level
        self.target_ip = ip
        self.main = main
        self.master = master
        threading.Thread.__init__(self, daemon=True)
        MastermindClientTCP.__init__(self)
        self.timer = datetime.now()  # timer for the keep Alive
        self.player_id = None
        self.connected = False

    def send_key(self, key):
        clientlog.info("Sending key Action %s to server" % key)
        data = json.dumps({'type': 'key_update', 'data': str(key)})
        self.send(data, compression=NetworkConnector.COMPRESSION)

    def run(self):
        clientlog.info("Connecting to ip %s" % str(self.target_ip))
        try:
            self.connect(self.target_ip, self.port)
            clientlog.info("Client connecting, waiting for initData")
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
            clientlog.info("Client got init Data, creating new Player") 
            contents = data['data']
            self.player_id = int(contents['player_id'])
            if self.master:
                self.main.network_connector.server.own_client = self.player_id

            for pl_center in contents['players']:
                try:
                    pid = int(pl_center.index('player_id'))
                except ValueError:
                    pid = len(self.level.players)
                # add the others
                self.level.add_player(pid, pl_center)
            # add ourself
            self.level.add_player(self.player_id)

            #kill removed sprites_removed
            removedSprite_ids_list = contents[Message.field_removed_sprites]
            tupeld = []
            for a in removedSprite_ids_list:
                tupeld.append((a[0], a[1]))
                
            self.level.physics.remove_sprites_by_id(tupeld)
            
            
            # tell the server that the client is init
            self.send_init_success()
            self.main.menu.show_menu(False)
        else:
            raise Exception('Did not get init as first Package') 

    def gold_removed(self, index):
        clientlog.info("Gold removed, notifing server")
        self.send_data_to_server(Message.type_gold_removed, index)

    def player_killed(self):
        clientlog.info("Player got killed sending to server")
        self.send_data_to_server(Message.type_player_killed, self.player_id)

    def send_init_success(self):
        """let the server know the connection succeeded"""
        data = {'player_id': self.player_id}
        self.send_data_to_server(Message.type_init, data)

    def send_data_to_server(self, message_type, py_data):
        data = json.dumps({'type': message_type, 'data': py_data})
        self.send(data, compression=NetworkConnector.COMPRESSION)

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
            clientlog.info("Got data from server: {}".format(str(data)))
            if data['type'] == Message.type_key_update:
                clientlog.info("got key_update from server")
                Controller.do_action(data['data']['key'], data['data']['player_id'])
                return

            if data['type'] == Message.type_bot_update:
                clientlog.info("got bot_update from server")
                Controller.bot_action(data['data']['key'], data['data']['bot_id'])
                return
            
            if data['type'] == Message.type_init:
                clientlog.info("got init succ")
                try:
                    self.level.players[int(data['data']['player_id'])]
                except IndexError:
                    pid = len(self.level.players)
                    self.level.add_player(pid)
                self.main.menu.show_menu(False)
                return

            if data['type'] == Message.type_client_dc:
                clientlog.info("A client disconnected, removing from game")
                pid = data['data']['client_id']
                if not self.level.remove_player(pid):
                    clientlog.error("Could not remove player form player list!")
                else:
                    clientlog.info("removed player form playerlist")
                return

            if data['type'] == Message.type_comp_update:
                clientlog.info("Sending own Pos to Server")
                self.send_current_pos_and_data()
                return

            if data['type'] == Message.type_comp_update_states:
                clientlog.info("Sending own states to Server")
                player = self.level.players[self.player_id]
                player_info = self.level.get_normalized_pos_and_data(player, False, False)
                self.send_data_to_server(Message.type_comp_update, player_info)
                return
            
            if data['type'] == Message.type_level_changed:
                clientlog.info("Got change level from Server")
                level_name = data[Message.field_level_name]
                self.level.load_level(level_name)
                return
            
            if data['type'] == Message.type_comp_update_set:
                '''don't set the positions on the server'''
                player_id, normalized_pos, is_bot, info = data['data']
                player_id = int(player_id)
                is_bot = bool(int(is_bot))

                if is_bot or player_id != self.player_id:
                    clientlog.debug("recieved player data: ", data['data'])
                    clientlog.info("Got pos setter from server")
                    clientlog.debug("setting player data: ", data['data'])
                    self.level.set_player_data(player_id, normalized_pos, is_bot, info)
                return

    def send_current_pos_and_data(self):
        """send the current position and state vars to the server"""
        try:
            player = self.level.players[self.player_id]
            player_info = self.level.get_normalized_pos_and_data(player, False)
            self.send_data_to_server(Message.type_comp_update, player_info)
        except IndexError:
            pass

            if data['type'] == Message.type_gold_removed:
                #Todo maybe remove gold if the sync is not working
                clientlog.info("Gold removed recieved from server, killing gold")
                WorldObject.kill_world_object(data['data'])
                return

            if data['type'] == Message.type_player_killed:
                clientlog.info("Got player killed from Server")
                pdb.set_trace()
                for player in self.level.players:
                    if player.player_id == data['data']:
                        player.kill()

    def send_keep_alive(self):
        """send keep alive if last was x seconds ago"""
        if (datetime.now() - self.timer).seconds > 4:
            data = json.dumps({'type': Message.type_keep_alive})
            self.send(data, compression=NetworkConnector.COMPRESSION)
            self.timer = datetime.now()
        pass


class Server(threading.Thread, MastermindServerTCP):

    """main network server"""
    def __init__(self, ip, port, level, main, local_only=False):
        self.ip = ip
        self.port = port
        self._level = level
        self.main = main
        self.local_only = local_only
        self.known_clients = []
        self.own_client = None
        self.connected = False
        self.sync_interval = 10  # seconds
        self.sync_time = datetime.now()
        self.sprites_removed = []
        threading.Thread.__init__(self, daemon=True)
        MastermindServerTCP.__init__(self, time_server_refresh=1, time_connection_refresh=1,
                                     time_connection_timeout=5.0)

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
        #adding ip to client list to generate the playerId
        if connection_object not in self.known_clients:
            srvlog.debug("Added client to known clients")
            self.known_clients.append(connection_object)
        #sending initial Data, to all clients so everyone is on the same page. TODO:  add info about enemies
        level_info = self.level.get_level_info_json()
        #the clients id
        misc_info = {'player_id': str(self.known_clients.index(connection_object)),
                     Message.field_removed_sprites : self.sprites_removed}
        #concat the data
        combined = {}
        for d in (level_info, misc_info):
            combined.update(d)
        
        data = json.dumps({'type': 'init', 'data': combined})

        self.callback_client_send(connection_object, data)


        #let the others know that there is a new client

        for client in self.known_clients:
            if client != connection_object:
                self.callback_client_send(client, data)

        '''get the up to date player positions'''
        self.send_to_all_clients(Message.type_comp_update)

        '''and up to date bot positions'''
        for bot in self.level.bots:
            '''update the bot positions only on the clients'''
            player_info = self.level.get_normalized_pos_and_data(bot, True)
            srvlog.debug("sending bot data: ", player_info)
            self.send_to_all_clients_except_self(Message.type_comp_update_set, player_info)
        
        return super(MastermindServerTCP, self).callback_connect_client(connection_object)

    def callback_disconnect_client(self, connection_object):
        """gets called if a client disconnects"""
        disconnected_client = self.known_clients.index(connection_object)
        srvlog.info("Client disconnected, sending to other clients %s" % disconnected_client)

        #kill the player of the disconnected client on all other clients
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
        data = {Message.field_level_name: level}
        self.send_to_all_clients(Message.type_level_changed, data)

    def send_to_all_clients(self, message, data=None):
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
        player_info = self.level.get_normalized_pos_and_data(bot, True)
        srvlog.debug("sending bot data: ", player_info)
        self.send_to_all_clients_except_self(Message.type_comp_update_set, player_info)

    def get_collected_data(self):
        collectedData = {}
        collectedData[Message.field_player_locations] = self.level.get_player_data()
        return collectedData
        
    @property
    def level(self):
        """return the current level"""
        return self._level

    @level.setter
    def level(self, level):
        self._level = level
        for client_id in range(len(self.known_clients)):
            self.level.add_player(client_id)
