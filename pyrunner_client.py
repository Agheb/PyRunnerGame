from Mastermind import *
import pyrunner_server

# The client's IP.  Modify to the server's IP on a LAN.  NAT punchthrough is not yet supported.
client_ip = "localhost"
# Tell the server to listen to all IPs, such as any IP within a LAN.
server_ip = "0.0.0.0"
# The port used for both the client and the server
port = 6317


def main():
    # global client, server, continuing

    client = MastermindClientTCP()
    try:
        print("Client connecting on \"" + client_ip + "\", port " + str(port) + " . . .")
        client.connect(client_ip, port)
    except MastermindError:
        print("No server found; starting server!")
        server = pyrunner_server.PyrunnerServer()
        server.connect(server_ip, port)
        server.accepting_allow()

        print("Client connecting on \"" + client_ip + "\", port " + str(port) + " . . .")
        client.connect(client_ip, port)
    print("Client connected!")

    texts = [
        "Hello world!  How are you today?",
        "I see you're well",
        "Lovely weather, methinks."
    ]
    for text in texts:
        print("Client: sending \"" + text + "\"")
        client.send(text, None)  # None for no compression

        reply = client.receive(True)  # True for blocking
        print("Client: got     \"" + str(reply) + "\"")

if __name__ == "__main__":
        main()
