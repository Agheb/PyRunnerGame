import threading, os, sys
import pdb
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir) 
from Mastermind import *

class NetworkConnector():

    
    def __init__(self):
        self.ip = "localhost"
        self.port = 6790
        pass
    def start_server_prompt(self):
        self.server = Server()
        self.master = True
    def join_server_prompt(self):
        self.master = False
        self.ip = input("Please enter an ip to connect to: ")
        self.client = Client(self.ip)



class Client(threading.Thread, MastermindClientTCP):
    def __init__(self, ip):
        threading.Thread.__init__(self)
        MastermindClientTCP.__init__(self)
        self.taget_ip = ip
    def run(self):
        self.connect(self.target_ip,NetworkConnector.port)
    def getResponse(self):
        self.last_reply = client.receive(True) #True for blocking
    def kill(self):
        self.disconnect()




class Server(threading.Thread, MastermindServerTCP):
    def __init__(self):
        threading.Thread.__init__(self) 
        MastermindServerTCP.__init__(self)
    def callback_client_handle(self, connection_object, data):
        print("Server got: \""+str(data)+"\"")
        self.callback_client_send(connection_object, data)
    def kill(self):
        self.accepting_disallow()
        self.disconnect_clients()
        self.disconnect()
    def run(self):
        self.connect("localhost",NetworkConnector.port)
        self.accepting_allow()






if __name__ == "__main__":
    con = NetworkConnector()
    #pdb.set_trace()
        
