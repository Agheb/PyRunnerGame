#!/usr/bin/python
# -*- coding: utf-8 -*-
# Python 2 related fixes
from __future__ import division
import threading
import logging
from pprint import pprint
import pdb
from .controller import Controller
from datetime import datetime
from time import sleep
import json
import socket
import textwrap
from Mastermind import *
from zeroconf import ServiceBrowser, ServiceStateChange, ServiceInfo, Zeroconf
from zeroconf import NonUniqueNameException, BadTypeInNameException
from .level_objecs import WorldObject
from .menu import MenuItem

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
        self.ip = "0.0.0.0"
        socket_ip = socket.gethostbyname(socket.gethostname())
        self.external_ip = socket_ip if not socket_ip.startswith("127.") else socket.gethostbyname(socket.getfqdn())
        self.main = main
        self.level = level
        self.port = START_PORT
        self.master = False
        self.client = None
        self.server = None
        self.browser = None
        self.advertiser = None

        print(str(self.ip), str(self.external_ip))

    def quit(self):
        """shutdown all threads"""
        try:
            self.server.kill()
            self.client.kill()
            self.browser.kill()
            self.advertiser.shutdown()
        except AttributeError:
            pass

    def init_new_server(self):
        """start a new server thread"""
        if self.server:
            self.server.kill()

        self.server = Server(self.ip, self.port, self.level, self.main)
        self.master = True
        self.server.start()

    def start_server_prompt(self, port=START_PORT):
        """starting a network server from the main menu"""

        self.port = port if port else START_PORT

        def start_server():
            """try to start a server"""

            if not self.server:

                self.init_new_server()

                while not self.server.connected:
                    '''give the thread 0.25 seconds to start (warning: this locks the main process)'''
                    sleep(0.25)

                    if not self.server.connected:
                        '''if it fails (e.g. port still in use) switch the port up to 5 times'''
                        if self.port < START_PORT + 5:
                            self.port += 1
                            self.init_new_server()
                            print("changing server and port to ", str(self.port))
                        else:
                            '''if it still fails give up'''
                            self.server.kill()
                            break
            else:
                self.join_server_prompt((self.ip, self.port))
                # self.main.load_level(self.main.START_LEVEL)

        print("starting server")
        start_server()

        if self.server and self.server.connected:
            self.join_server_prompt((self.ip, self.port))
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
        print(str(ip))

        if isinstance(ip, str):
            '''let the computer resolve the hostname to an ip'''
            ip = socket.gethostbyname(ip)
        '''change to localhost ip if we are on the same computer'''
        self.ip = ip    # "127.0.0.1" if self.ip == self.external_ip else ip

        print(str(ip))

        def init_new_client():
            """start a new client thread"""
            if self.client:
                self.client.kill()

            self.client = Client(self.ip, self.port, self.level, self.main)
            self.master = False
            self.client.start()

        def join_server():
            """join your own or another server"""

            init_new_client()

            # while not self.client.connected:
            #     '''give the thread 0.25 seconds to start (warning: this locks the main process)'''
            #     sleep(0.5)
            #
            #     if not self.client.connected:
            #         '''if it fails (e.g. no server running on this port) switch the port up to 5 times'''
            #         if self.port < START_PORT + 5:
            #             self.port += 1
            #             self.client.port = self.port
            #             print("changing client and port to ", str(self.port))
            #         else:
            #             '''if it still fails give up'''
            #             self.client.kill()
            #             break
            #         # init_new_client()

            # self.ip = input("Please enter an ip to connect to: ")

        if self.client and self.client.connected:
            '''disconnect from other servers first'''
            self.client.disconnect()

        join_server()

        if self.client and self.client.connected:
            print("connected to %s" % self.ip)

    def update(self):
        try:
            self.client.update()
        except (MastermindErrorClient, AttributeError):
            pass


class ZeroConfAdvertiser(object):
    """propagate network server via zeroconf multicast"""

    def __init__(self, ip, port):
        self.id = 0
        self.ip = ip
        self.port = port
        self.listener = Zeroconf()
        self.hostname = socket.gethostname()
        self.gamename = self.hostname + "_pyrunner._tcp.local."
        self.desc = {'game': 'pyRunner v1.0'}
        self.info = ServiceInfo("_pyrunner._tcp.local.", self.gamename, socket.inet_aton(self.ip),
                                self.port, 0, 0, self.desc, self.hostname)
        '''propagate the server'''
        self.server()

    def server(self):
        """propagate your own server"""
        try:
            self.listener.register_service(self.info)
        except NonUniqueNameException:
            try:
                self.id += 1
                self.gamename = "%s.%s" % (self.id, self.gamename)
                self.hostname = "%s.%s" % (self.id, self.hostname)
                self.info = ServiceInfo("_pyrunner._tcp.local.", self.gamename, socket.inet_aton(self.ip),
                                        self.port, 0, 0, self.desc, self.hostname)
                self.listener.register_service(self.info)
            except BadTypeInNameException:
                pass

    def shutdown(self):
        """stop service advertisement"""
        self.listener.unregister_service(self.info)
        self.listener.close()


class ZeroConfListener(threading.Thread):
    """browse for network servers via zeroconf multicast"""

    def __init__(self, menu, network_connector, ip, port):
        threading.Thread.__init__(self, daemon=True)
        self.menu = menu
        self.network_connector = network_connector
        self.id = 0
        self.ip = ip
        self.port = port
        self.listener = Zeroconf()
        self.browser = None
        self.hostname = socket.gethostname()
        self.gamename = self.hostname + "_pyrunner._tcp.local."
        self.desc = {'game': 'pyRunner v1.0'}
        self.info = ServiceInfo("_pyrunner._tcp.local.", self.gamename, socket.inet_aton(self.ip),
                                self.port, 0, 0, self.desc, self.hostname)

    def shutdown(self):
        """stop service advertisement"""
        self.listener.close()

    def kill(self):
        """quit this process"""
        self.shutdown()

    def run(self):
        """main function"""
        if self.browser:
            if self.network_connector.client and self.network_connector.client.connected:
                '''shutdown the browser if the user is in a game'''
                self.kill()

        sleep(1)

    def start_browser(self):
        """browse for games"""
        self.browser = ServiceBrowser(self.listener, "_pyrunner._tcp.local.", handlers=[self.on_service_state_change])
        self.menu.network.flush_all_items()
        self.menu.set_current_menu(self.menu.network)

    def on_service_state_change(self, zeroconf, service_type, name, state_change):
        """check for new services"""

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info:
                ip = socket.inet_ntoa(info.address)
                address = ip if not ip.startswith("127.") else info.server
                port = info.port
                print(str(address), ":", str(port))
                menu_item = MenuItem(info.server, self.network_connector.join_server_prompt, vars=(address, port))
                '''add the full name as id so it can be removed if the server goes offline'''
                menu_item.id = name
                self.menu.network.add_item(menu_item)
                self.menu.show_menu(True)

        if state_change is ServiceStateChange.Removed:
            '''remove the item from the menu and refresh it if the user still has it open'''
            self.menu.network.delete_item(name)
            if self.menu.in_menu:
                '''refresh the menu'''
                self.menu.show_menu(True)


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

    def network_error_menu(self, error_string):
        """show errors in the menu"""

        if not isinstance(error_string, list):
            '''split longer text into multiple items'''
            len_per_line = 30
            error_string = textwrap.wrap(error_string, len_per_line, break_long_words=False)

        self.main.menu.network.flush_all_items()
        for text in error_string:
            self.main.menu.network.add_item(MenuItem(text, None))
        self.main.menu.set_current_menu(self.main.menu.network)
        self.main.menu.show_menu(True)

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
        except (OSError, MastermindErrorSocket):
            self.network_error_menu("An error occurred connecting to the server. Please try again later.")
            pass
            # self.port = self.port + 1 if self.port and self.port < START_PORT else START_PORT

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
        try:
            self.disconnect()
        except AttributeError:
            pass
        self.connected = False

    def update(self):
        """run the server"""
        self.send_keep_alive()
        raw_data = self.receive(False)

        # TODO sync world object state over network
        # .pop(0) removes the first item in a list (FIFO with .append)
        # and automatically empties the list
        if WorldObject.network_kill_list:
            for index in WorldObject.network_kill_list.pop(0):
                pass
                # TODO send index (list) to all clients
                # TODO all clients should then call
                # WorldObject.kill_world_object(index)

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
    def __init__(self, ip, port, level, main):
        self.ip = ip
        self.port = port
        self._level = level
        self.main = main
        self.known_clients = []
        self.connected = False
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
            print(str(OSError))
            print(str(MastermindErrorSocket))
            pass
            # self.port = self.port + 1 if self.port and self.port < START_PORT else START_PORT
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
