#!/usr/bin/python
# -*- coding: utf-8 -*-
"""advertise the server over the network using Bonjour/Zeroconf"""

import threading
import socket
from zeroconf import ServiceBrowser, ServiceStateChange, ServiceInfo, Zeroconf
from zeroconf import NonUniqueNameException, BadTypeInNameException
from time import sleep
from pyrunner_classes import MenuItem


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
