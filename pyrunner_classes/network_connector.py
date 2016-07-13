#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Main Network Handler Class"""
# Python 2 related fixes
from __future__ import division

import socket

from time import sleep
from pyrunner_classes import logging, Player
from pyrunner_classes.network_server import Server
from pyrunner_classes.network_client import Client
from pyrunner_classes.zeroconf_bonjour import ZeroConfAdvertiser, ZeroConfListener
from pyrunner_classes.network_shared import *

START_PORT = 6799
net_log = logging.getLogger("Network")


class NetworkConnector(object):
    """the main network class"""

    def __init__(self, main):
        self.ip = "0.0.0.0"
        self.socket_ip = socket.gethostbyname(socket.gethostname())
        self.network_ip = self.get_network_ip()
        self.external_ip = self.socket_ip
        self.main = main
        self.port = START_PORT
        self.master = False
        self.client = None
        self.server = None
        self.browser = None
        self.advertiser = None
        self.local_game = False
        self.register_physics_callback()

        '''get IP'''
        if self.socket_ip.startswith("127."):
            if not self.network_ip.startswith("127."):
                self.external_ip = self.network_ip
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

    def clear_level(self):
        """remove all level states for a clean start"""
        self.main.level.flush_network_players()
        self.main.level.prepare_level_change()
        self.main.load_level()

    def init_new_server(self, local_only=False):
        """start a new server thread"""
        if self.server:
            self.server.kill()
            self.clear_level()

        self.server = Server(self.ip, self.port, self.main, local_only)
        self.master = True
        self.server.start()

    def register_physics_callback(self):
        """adds the network connector to the physics"""
        self.main.level.physics.register_callback(self)

    def start_local_game(self):
        """run a single player game"""
        self.start_server_prompt(START_PORT - 10, True)

    def start_server_prompt(self, port=START_PORT, local_only=False):
        """starting a network server from the main menu"""
        self.ip = "0.0.0.0" if not local_only else "127.0.0.1"
        self.port = port if port else START_PORT
        self.local_game = local_only

        def start_server():
            """try to start a server"""
            self.init_new_server(local_only)

            while not self.server.connected:
                '''give the thread 0.25 seconds to start (warning: this locks the main process)'''
                sleep(0.25)

                if not self.server.connected:
                    '''if it fails (e.g. port still in use) switch the port up to 5 times'''
                    if self.port < START_PORT + 5:
                        self.port += 1
                        self.init_new_server()
                        net_log.info("changing server and port to ", str(self.port))
                    else:
                        '''if it still fails give up'''
                        self.server.kill()
                        break

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
        ip, port = ip_and_port

        if isinstance(ip, str):
            '''let the computer resolve the hostname to an ip'''
            ip = socket.gethostbyname(ip)

        if self.client and (self.client.target_ip == ip or self.external_ip == ip)\
                and self.port == port and not self.local_game and not self.main.game_over and self.client.connected:
            self.main.menu.network.print_error("You are already connected to this server")
            return

        self.ip = ip
        self.port = port

        if self.server and self.server.ip != ip:
            self.server.kill()
            self.master = False
            if self.advertiser:
                self.advertiser.shutdown()

        '''start a new client thread'''
        if self.client:
            '''disconnect from other servers first'''
            self.client.kill()
            self.clear_level()

        self.client = Client(self.ip, self.port, self.main, self.master)
        self.client.start()

        if self.client and self.client.connected:
            net_log.info("connected to %s" % self.ip)

    def update(self):
        """update function that get's called by the main class"""
        try:
            self.client.update()
            self.server.update()
        except (MastermindErrorClient, AttributeError):
            pass
