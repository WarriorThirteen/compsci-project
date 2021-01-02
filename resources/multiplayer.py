##  IMPORTS

#  import game
class test_game:
    '''
    Test class to simulate running of the game and gathering it's data from a thread
    '''
    def __init__(self):
        self.count = 1
        self.randomness_seed = 1234
        self.dot_loc_list = [(1,1), (2,1)]
        self.blobs = {}

    def run(self):
        while True:
            self.count += 1
            if self.count >= 60:
                self.count = 1

            time.sleep(0.05)

    def create_blob(self, controller, id):
        self.blobs[id] = "blob"

game = test_game()

import socket
import threading
import time

from datetime import datetime

##  Plan is we import game and run it from here during multiplayer
##  Then access attributes and send them to connected people


# seperator token to divide parts of message and buffer is how large each message is.
SEPERATOR = "<seperator>"
BUFFER_SIZE = 4096


# Set greetings for new players:
first_connection_message = "First time connection"
add_to_list_message = "Add me to your client list"
disconnecting_message = "I am off, please forget me"


# Set addresses and port number:
# We are using peer to peer so no host
MY_ADDRESS = "0.0.0.0"
PORT = 5001


# Set of connected client sockets for sending data
# and connected addresses to send to new clients
connected_clients = set()
connected_addresses = set()


# Control / Configuration variables
MAX_CONNECTIONS = 5



##  GENERATE DATA PACKET FUNCTIONS


def gen_intro_packet():
    '''
    Generate and return a packet for new players.
    This packet should contain the randomness seed, current random_count, connected player addresses, and the dot location list.
    Other player addresses seperated from rest of packets by two seperators
    '''
    packet = ""
    packet += str(game.randomness_seed)
    packet += SEPERATOR
    packet += str(game.count)
    packet += SEPERATOR
    packet += str(game.dot_loc_list)
    packet += SEPERATOR

    for i in connected_addresses:
        packet += SEPERATOR
        packet += str(i)

    return packet





# First thread: run game

def game_box():
    game.run()


# Second thread: listen for new people

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
        connected_clients.add(new_socket)
        connected_addresses.add(address)

        # Start listening to client for new info
        new_thread = threading.Thread(target=listen_to, args=(address, new_socket,))
        new_thread.daemon = True
        new_thread.start()





    # close socket
    s_listener.close()


# Third thread: Listen to the connected clients:

def listen_to(client_address, client_socket=None, mode="receive"):
    '''
    Receive an address from function call.
    Connect to address if mode is "introduce"
    Perform the handshake, and then create a new blob for this player.
    Control the player's blob depending on their messaged actions.

    2 Modes:
    introduce: for when we connect to the client
    receive: for when a new client connects to us

    introduce does not need a client_socket to be provided
    '''
    go = True
    if client_socket == None:
        mode = "introduce"

    try:    # Greet the new contact


        if mode == "receive": # We are receiving a message from a new client:
            # Receive introduction for handshake
            greeting = client_socket.recv(BUFFER_SIZE).decode()

            if greeting == first_connection_message:
                # send intro info to new player
                client_socket.send(gen_intro_packet().encode())

            elif greeting == add_to_list_message:
                # They are added to our list when they connect to us
                pass

            # Create a blob for this player
            game.create_blob("networked", client_address)


    
        elif mode == "introduce":
            # We need to say hello and receive data about the game and other players:
            client_socket.send(first_connection_message.encode())
            game_data, other_clients = client_socket.receive(BUFFER_SIZE).decode().split((SEPERATOR + SEPERATOR))


            # Greet the other clients
            for address in other_clients:
   


                ######### I NEED TO CONNECT TO NEW CLIENT, CAN ONE SOCKET CONNECT MULTIPLE TIMES 
                new_socket = sock

                # Start listening to client for new info
                new_thread = threading.Thread(target=listen_to, args=(new_socket, address, "greet",))
                new_thread.daemon = True
                new_thread.start()



            # configure our game based on data:
            game_data.split(SEPERATOR)
            pass # TODO

        


    except Exception as e: # Client disconnected during meeting sequence
        go = False
        print(f"Error encountered: {e}")

    






##  Main Loop
def main():
    

    # thread 1 - Run game thread
    game_thread = threading.Thread(target=game_box)
    game_thread.daemon = True
    game_thread.start()


    while game.count != 59:
        print(game.count)

    # print(socket.gethostbyname(socket.gethostname())) Prints ip address of this computer





if __name__ == "__main__":
    main()