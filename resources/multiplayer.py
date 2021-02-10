##  IMPORTS

from resources import game as gm

import socket
import threading
import time


##  Plan is we import game and run it from here during multiplayer
##  Then access attributes and send them to connected people


# SEPARATOR token to divide parts of message and buffer is how large each message is.
SEPARATOR = "<SEPARATOR>"
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


# Control / Configuration variables
MAX_CONNECTIONS = 5



##  For Hosting


def gen_intro_packet():
    '''
    Generate and return a packet for new players.
    This packet should contain the randomness seed, current random_count, connected player addresses, and the dot location list.
    '''
    # Wait until game has started
    game.running_flag.wait()

    # Now provide details
    packet = SEPARATOR.join(game.info_for_new())

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


    game.running_flag.wait()

    while game.running_flag.isSet():
        # Accept incoming connections
        new_socket, address = s_listener.accept()

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
    # This will only return after the game has begun
    client_socket.send(gen_intro_packet().encode())

    # Client is currently connected
    connected = True


    # Add new client to list of client sockets
    # We add them to the set here, so we don't send them data before they have configured their game
    connected_client_sockets.add(client_socket)


    # Generate this player a blob:
    game.create_blob(client_address)

    # Tell clients a new player has joined:
    msg = SEPARATOR.join((new_connection_message, client_address))
    for client in connected_client_sockets:
        if client != client_socket:
            client.send(msg.encode())



    # Now we do a loop of receiving and resending:
    while game.running_flag.isSet() and connected:
        # Listen for message
        msg_list = client_socket.recv(BUFFER_SIZE).decode().split(EOM_TOKEN)


        for msg in msg_list:
            # We may have received a blank message
            if msg:

                # Player is leaving the game
                if msg == disconnecting_message:
                    game.disconnect_blob(client_address)
                    connected_client_sockets.remove(client_socket)

                    # tell other players this player has left:
                    msg = disconnecting_message + SEPARATOR + client_address + EOM_TOKEN
                    for client in connected_client_sockets:
                        client.send(msg.encode())

                    connected == False

                    break

                # Process message for our game
                process_game_info(msg.removesuffix(EOM_TOKEN))

                # Resend message to our other clients:
                while True:         # if message is disconnecting message, it is important that it is sent
                    try:
                        for client in connected_client_sockets:
                            if client != client_socket:          # don't send message back to sender
                                client.send(msg.encode())
                        break

                    except RuntimeError: # a different client disconnected while sending
                        pass


# We need a seperate thread for sending out our own data.
# This way we can stop and handle our own issues properly
# in the same way clients can i.e. closing the game etc.

def broadcast_from_server():
    '''
    Every few milliseconds, send our data to our clients.
    This happens in a thread to handle exceptional circumstances such as when
    the host closes the game.
    '''
    # time.sleep(3) # So we don't start sending data before game starts
    game.running_flag.wait()

    while game.running_flag.isSet():
        msg = game.data_to_send() + EOM_TOKEN

        try:
            for client in connected_client_sockets:
                client.send(msg.encode())

        except RuntimeError: # Client was removed from list while we were iterating through
            pass

        time.sleep(1 / game.UPS)

    # TODO end game without crash, Maybe designate new host?
    print("[MULTIPLAYER]:Broadcast stopped")



##  For connecting to a Host


def connect_to_server(server_address):
    '''
    Create a socket and connect to a server with a provided address.
    Receive info packet from server and configure game appropriately.
    '''

    # connect to server
    s = socket.socket()
    s.connect((server_address, PORT))

    # Receive data until end of welcome packet:
    intro_packet = s.recv(BUFFER_SIZE).decode().split(SEPARATOR)

    # Configure game with welcome packet
    game.configure_game(intro_packet)

    return s


def listen_to_server(s):
    '''
    Listen to the server for messages
    and take appropriate action
    '''
    game.running_flag.wait()
    while game.running_flag.isSet():
        msg_list = s.recv(BUFFER_SIZE).decode().split(EOM_TOKEN)    # Prevent multiple messages conjoining in a buffer

        for msg in msg_list:
            # In case we receive a blank message
            if msg:

                if msg[0] == new_connection_message:
                    # A new player has connected
                    # so make them a blob in our game
                    game.create_blob(msg[1])

                elif msg[0] == disconnecting_message:
                    # A player has disconnected
                    game.disconnect_blob(msg.split(SEPARATOR)[1])

                else:
                    # Message is game info
                    process_game_info(msg.removesuffix(EOM_TOKEN))



def broadcast_to_server(s):
    '''
    Every few milliseconds, send our data to the server.
    This happens here as pygame is not thread safe
    '''
    # time.sleep(1) # So we don't start sending data before game starts
    game.running_flag.wait()

    while game.running_flag.isSet():
        msg = game.data_to_send() + EOM_TOKEN
        s.send(msg.encode())
        time.sleep(1 / game.UPS)

    s.send(disconnecting_message.encode())





# UTILITY

# Use info we receive about game actions
def process_game_info(message):
    '''
    Process received game data into gameplay
    '''
    game.process_player_move(message)



##  GENERIC FUNCTIONS FOR EXTERNAL USE

def join(server_address):
    '''
    Connect to and play with people on a server
    '''

    # Tell the game that we have are not the host
    game.host_name = server_address.split(".")[-1]

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


    # Now run the configured game
    game.run()


    # Give disconnnect message a chance
    time.sleep(0.5)

    # Game Over :(
    s.close()




def host():
    '''
    Host a server for others to join
    '''

    print("[MULTIPLAYER]:HOSTING")

    # Start Listening

    # listening = threading.Event()
    # listening.set()

    listener_thread = threading.Thread(target=listen_for_clients)
    listener_thread.daemon = True
    listener_thread.start()
    print("[MULTIPLAYER]:Started Listening")


    # Setup to send our data to our clients

    sender_thread = threading.Thread(target=broadcast_from_server)
    sender_thread.daemon = True
    sender_thread.start()
    print("[MULTIPLAYER]:Beginning to broadcast game data")


    # Run our game
    game.run()




if __name__ == "__main__":

    
    game = gm.game()
    game.set_multiplayer()

    host()
    # join("192.168.0.70")