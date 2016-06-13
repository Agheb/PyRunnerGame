import threading, os, sys, logging
from pprint import pprint
import pdb
import json
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
from Mastermind import *

class NetworkConnector():

    
    def __init__(self):
        self.ip = "localhost"
        self.port = 6791
    def start_server_prompt(self):
        self.server = Server(self.port)
        self.master = True
        self.server.start()
    def join_server_prompt(self):
        self.master = False
        #self.ip = input("Please enter an ip to connect to: ")
        self.client = Client("localhost", self.port)
        self.client.start()



class Client(threading.Thread, MastermindClientTCP):
    def __init__(self, ip, port):
        self.port = port
        self.target_ip = ip
        threading.Thread.__init__(self)
        MastermindClientTCP.__init__(self)
    def run(self):
        #pdb.set_trace()
        logging.info("Connecting to ip %s" %str(self.target_ip))
        self.connect(self.target_ip,self.port)
        logging.info("Client connecting, waiting for initData")
        self.waitForInitData()
    def getResponse(self):
        self.last_reply = client.receive(True) #True for blocking
    def waitForInitData(self):
        initData = self.receive(True)
        json.loads(initData)
        pprint(initData)
    def kill(self):
        self.disconnect()




class Server(threading.Thread, MastermindServerTCP):
    def __init__(self,port):
        self.port = port
        threading.Thread.__init__(self) 
        MastermindServerTCP.__init__(self)
    def callback_client_handle(self, connection_object, data):
        print("Server got: \""+str(data)+"\"")
        self.callback_client_send(connection_object, data)
    def callback_connect_client(self, connection_object):
        logging.info("New Client Connected!")
        #TODO insert initial data here
        data = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])
        self.callback_client_send(connection_object, data)
        return super(MastermindServerTCP,self).callback_connect_client(connection_object)
    def kill(self):
        self.accepting_disallow()
        self.disconnect_clients()
        self.disconnect()
    def run(self):
        self.connect("localhost",self.port)
        self.accepting_allow()
        logging.info("server started and accepting connections")






if __name__ == "__main__":
    con = NetworkConnector()
    #pdb.set_trace()
        
