##  IMPORTS

import game as gm

class test_game:
    '''
    Test class to simulate running of the game and gathering it's data from a thread
    '''
    def __init__(self):
        self.count = 1
        self.randomness_seed = 1234
        self.dot_loc_list = [(1,1), (2,1)]
        self.blobs = {}
        self.UPS = 20


    def run(self):
        while True:
            self.count += 1
            if self.count >= 60:
                self.count = 1

            time.sleep(0.05)


    def configure_game(self, config):
        '''
        Configure the game setup to mimic someone else's game.
        '''
        pass
    

    def create_blob(self, identity, controller):
        self.blobs[identity] = "blob"


    def info_for_new(self):
        '''
        return array of info for a new player
        '''
        return (self.randomness_seed, self.count, self.dot_loc_list, self.blobs)


    def data_to_send(self):
        '''
        Generate data to send to the server
        '''
        return "Yes"


    def process_player_move(self, data):
        '''
        Process an update for movement of a player blob
        '''
        pass


    def disconnect_blob(self, identity):
        '''
        Disconnect a networked blob controller and delete their blob
        '''
        del self.blobs[identity]
    



game = gm.game()

import socket
import threading
import time

from datetime import datetime

##  Plan is we import game and run it from here during multiplayer
##  Then access attributes and send them to connected people


# seperator token to divide parts of message and buffer is how large each message is.
SEPERATOR = "<seperator>"
EOM_TOKEN = "<end>"
BUFFER_SIZE = 4096


# Set greetings for new players:
new_connection_message = "+"
# add_to_list_message = "+"   We are client server now
disconnecting_message = "X"


# Set addresses and port number:
MY_ADDRESS = "0.0.0.0"
PORT = 5001


# Set of connected client sockets for sending data in server mode
# and connected addresses to send to new clients and record who we expect info about
connected_client_sockets = set()
connected_addresses = set()


# Control / Configuration variables
MAX_CONNECTIONS = 5
DELAY_BETWEEN_SEND = 0.1



##  GENERATE DATA PACKET FUNCTION


def gen_intro_packet():
    '''
    Generate and return a packet for new players.
    This packet should contain the randomness seed, current random_count, connected player addresses, and the dot location list.
    '''
    packet = SEPERATOR.join(game.info_for_new())

    return packet



# Thread to run game

# def game_box():
#     game.run()  ## PYGAME IS NOT THREAD SAFE


# Listen for new people

def listen_for_clients():
    '''
    Listen on the socket.
    When a new client attempts to connect, record their details and set up a listener thread for them
    '''
    # create socket
    s_listener = socket.socket()
    s_listener.bind((MY_ADDRESS, PORT))


    s_listener.listen(5)

    while True:
        # Accept incoming connections
        new_socket, address = s_listener.accept()

        # Add new client to list of client sockets
        connected_client_sockets.add(new_socket)
        connected_addresses.add(address)

        # Start listening to client for new info
        new_thread = threading.Thread(target=client_connector, args=(address[0], new_socket,))
        new_thread.daemon = True
        new_thread.start()



    # close socket
    s_listener.close()


# Listen to the connected clients:

def client_connector(client_address, client_socket):
    '''
    Function to receive data from a client.
    Client will be sent information about the current game.
    Client will then be allowed to send information about their activities,
    which will be sent to all other clients
    and will be continuosly sent data from other clients for their game.
    '''
    
    # Step one send new client game data:
    client_socket.send(gen_intro_packet().encode())


    # Generate this player a blob:
    game.create_blob(client_address, "networked")

    # Tell clients a new player has joined:
    msg = SEPERATOR.join((new_connection_message, client_address))
    for client in connected_client_sockets:
        if client != client_socket:
            client.send(msg.encode())


    # Now we do a loop of receiving and resending:
    while True:
        # Listen for message
        msg_list = client_socket.recv(BUFFER_SIZE).decode().split(EOM_TOKEN)

        # When we receive a message, send back our data:
        client_socket.send()

        for msg in msg_list:

            # Player is leaving the game
            if msg == disconnecting_message:
                game.disconnect_blob(client_address)

                # tell other players this player has left:
                msg = disconnecting_message + SEPERATOR + client_address

            # Process message for our game
            process_game_info(msg.removesuffix(EOM_TOKEN))

            # Resend message to our other clients:
            for client in connected_client_sockets:
                if client != client_socket:          # don't send message back to sender
                    client.send(msg.encode())


    
def connect_to_server(server_address):
    '''
    Create a socket and connect to a server with a provided address.
    Receive info packet from server.
    '''

    # connect to server
    s = socket.socket()
    s.connect((server_address, PORT))

    # Receive data until end of welcome packet:
    intro_packet = s.recv(BUFFER_SIZE).decode().split(SEPERATOR)

    # Configure game with welcome packet
    game.configure_game(intro_packet) # TODO

    return s


def listen_to_server(s):
    '''
    Listen to the server for messages
    and take appropriate action
    '''
    while True:
        msg_list = s.recv(BUFFER_SIZE).decode().split(EOM_TOKEN)    # Prevent multiple messages conjoining in a buffer

        for msg in msg_list:
            msg = msg.split(SEPERATOR)
            if msg[0] == new_connection_message:
                # A new player has connected
                # so make them a blob in our game
                game.create_blob(msg[1], "networked")

            elif msg[0] == disconnecting_message:
                # A player has disconnected
                game.disconnect_blob(msg[1])

            else:
                # Message is game info
                process_game_info(msg[0].removesuffix(EOM_TOKEN))



def broadcast_to_server(s):
    '''
    Every few milliseconds, send our data to the server.
    This happens here as pygame is not thread safe
    '''
    time.sleep(1) # So we don't start sending data before game starts

    while True:
        msg = game.data_to_send() + EOM_TOKEN
        if msg == "End":         # TODO end game without crash
            break
        s.send(msg.encode())
        time.sleep(1 / game.UPS)



# Use info we receive about game actions
def process_game_info(message):
    '''
    Process received game data into gameplay
    '''
    if message:
        game.process_player_move(message)
    




##  GENERIC FUNCTIONS FOR EXTERNAL USE

def join(server_address):
    '''
    Connect to and play with people on a server
    '''
    print("[MULTIPLAYER]:JOINING")

    # Generate socket connected to server and configure game
    s = connect_to_server(server_address)




    # Setup thread to continuously listen to server for updates
    server_listener = threading.Thread(target=listen_to_server, args=(s,))
    server_listener.daemon = True
    server_listener.start()


    # every time tick send our data to the server
    # this went to broadcast func as pygame needs to be run here
    server_sender = threading.Thread(target=broadcast_to_server, args=(s,))
    server_sender.daemon = True
    server_sender.start()

    # game_started = threading.Event()
    # game_started.clear()




    # Now run the configured game
    game.run()



    # Game Over :(
    s.close()




def host():
    '''
    Host a server for others to join
    '''
    print("[MULTIPLAYER]:HOSTING")


    # # Start Listening
    # listening = threading.Event()
    # listening.set()
    

    listener_thread = threading.Thread(target=listen_for_clients)
    listener_thread.daemon = True
    listener_thread.start()
    print("[MULTIPLAYER]:Started Listening")


    # Run our game
    game.run()

    # # Simple stop hosting system
    # input()
    # listening.clear()



if __name__ == "__main__":
    
    # host()
    # join("192.168.0.70")