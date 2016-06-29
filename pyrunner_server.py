from Mastermind import *
import threading
from time import strftime, gmtime

# The client's IP.  Modify to the server's IP on a LAN.  NAT punchthrough is not yet supported.
client_ip = "localhost"
# Tell the server to listen to all IPs, such as any IP within a LAN.
server_ip = "0.0.0.0"
# The port used for both the client and the server
port = 6317

class PyrunnerServer( MastermindServerTCP ):


    def __init__(self):
        MastermindServerTCP.__init__(self,0.5,0.5,10.0)

        self.mutex = threading.lock()
        self.chat = [None] * 100 # Warum ? 100x  Es wird wohl ein Array mit 100 Einträgen erstellt



    def add_message(self, msg):
        timestamp = strftime("%H:%M:%S", gmtime())

        self.mutex.acquire() #
        self.chat = self.chat[1:] + [timestamp + " | " + msg] # Datenstruktur Array zur Sicherung der Einträge
        self.mutex.release()


