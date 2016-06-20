import threading, os, sys, logging
from pprint import pprint
import pdb
import json
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
from Mastermind import *



class NetworkConnector():
    COMPRESSION = None
    
    def __init__(self, physics):
        self.ip = "localhost"
        self.physics = physics
        self.port = 6794
    def start_server_prompt(self):
        self.server = Server(self.port)
        self.master = True
        self.server.start()
    def join_server_prompt(self):
        self.master = False
        #self.ip = input("Please enter an ip to connect to: ")
        self.client = Client("localhost", self.port, self.physics)
        self.client.start()



class Client(threading.Thread, MastermindClientTCP):
    def __init__(self, ip, port, physics):
        self.port = port
        self.physics = physics
        self.target_ip = ip
        threading.Thread.__init__(self)
        self.daemon = True
        MastermindClientTCP.__init__(self)
    def send_key(self, key):
        logging.info("Sending key Action %s to server" % key)
        data = json.dumps({'type': 'key_update','data':str(key)})
        self.send(data, compression = NetworkConnector.COMPRESSION)
    def run(self):
        logging.info("Connecting to ip %s" %str(self.target_ip))
        self.connect(self.target_ip,self.port)
        logging.info("Client connecting, waiting for initData")
        self.connected = True
        self.waitForInitData()
    def get_last_command(self):
        #for now, maybe we need non blocking later
        raw_data = self.receive(True)
        data = json.loads(raw_data)
        logging.info("Go data from server")
        if data['type'] == 'key_update':
            logging.info("got key_update from server")
            return data['data'], data['player_id']
    def waitForInitData(self):
        initData_raw = self.receive(True)
        data = json.loads(initData_raw)
        if data['type'] == 'init':
            logging.info("Client got init Data, creating new Player") 
            self.player_id = data['player_id']
            self.physics.add_player()
        else:
            raise Exception('Did not get init as first Package') 
    def kill(self):
        self.disconnect()
        self.connected = False




class Server(threading.Thread, MastermindServerTCP):
    def __init__(self,port):
        self.port = port
        self.known_clients = []
        threading.Thread.__init__(self) 
        MastermindServerTCP.__init__(self)
        self.daemon = True

    def callback_client_handle(self, connection_object, data):
        """Initial point of data arrival. Data is received and passed on"""
        logging.info("Server got: '%s'" %str(data))
        json_data = json.loads(data)
        self.interpret_client_data(json_data, connection_object)
        self.callback_client_send(connection_object, data)

    def interpret_client_data(self, data, con_obj):
        """interprets data send from the client to the server"""
        if data['type'] == "key_update":
            logging.info("Got key Update from Client")
            self.send_key(data['data'], self.known_clients.index(con_obj))
        if data['type'] == "complete_update":
            logging.info("Got full update from Client")
            pass

    def callback_connect_client(self, connection_object):
        """this methods gets called on initial connect of a client"""
        logging.info("New Client Connected %s" %str(connection_object.address))
        #adding ip to client list to generate the playerId
        if connection_object not in self.known_clients:
            self.known_clients.append(connection_object)
        #sending initial Data TODO: put inside data object,  add info about enemies, other players pos...
        data = json.dumps({'type': 'init','player_id': str(self.known_clients.index(connection_object))})
        self.callback_client_send(connection_object, data)
        return super(MastermindServerTCP,self).callback_connect_client(connection_object)

    def send_key(self, key, player_id):
        """puts a passed key inside a json object and sends it to all clients"""
        logging.info("Sending key {} to Client with id {}".format(str(key), str(player_id)))
        data = json.dumps({'type': 'key_update','data':str(key), 'player_id': str(player_id)})
        connection_object = self.known_clients[player_id]
        self.callback_client_send(connection_object, data)
    def kill(self):
        self.accepting_disallow()
        self.disconnect_clients()
        self.disconnect()
    def run(self):
        self.connect("localhost",self.port)
        self.accepting_allow()
        logging.info("server started and accepting connections")
    def callback_disconnect(self):
        logging.info("Server disconnected from network")
        return super(MastermindServerTCP,self).callback_disconnect()
