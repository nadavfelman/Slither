import math
import random
import socket
import threading

import pygame

import connection.protocol as protocol
import game


# initial all the variables
clients = {}
clientsLock = threading.Lock()
game_data = game.dataSets.ServerDataBase()
dataLock = threading.Lock()
clock = pygame.time.Clock()

# the limit of the angle change for the players
ANGLE_LIM = math.pi * 0.02


class ClientConnection(threading.Thread):
    """
    this is the thread who communicates with a client.
    this thread is synchronous so it handles coming messages and sending messages
    """

    def __init__(self, client_socket, client_addr):
        """
        initializes the variables to the thread.

        Args:
            client_socket (socket.socket): the socket used ti communicate with a client
            client_addr (tuple): the address of the client
        """
        super(ClientConnection, self).__init__()
        self.client_addr = client_addr
        self.client_socket = client_socket
        self.key = protocol.key(self.client_socket)

    def run(self):
        """
        the "main" of the ClientConnection thread.
        this thread communicates with the client.

        this includes:
            - startup communication
            - updating the client about changes (only sending the updates)
            - updating the server about the client actions
        """
        """
        initial connection:
        - run only once
        - no timeout
        """
        print 'New Client Connected. address: {}'.format(self.client_addr)

        # set timeout to be None for the startup communication
        self.client_socket.settimeout(None)

        # add the client to the client dict
        # this ensures the client will get massages from the server
        with clientsLock:
            clients[self.key] = []

        # send server initial
        protocol.send_data(self.client_socket, protocol.initial_server(game_data.board.width, game_data.board.height, self.key))

        # get client initial
        while True:
            data = protocol.recv_data(self.client_socket)
            data = protocol.parse(data)
            if data['type'] == protocol.Type.INITIAL and \
                    data['subtype'] == protocol.Subtype.INITIAL.client:
                name = data['name']
                break

        # send client current state
        # this adds all the current game objects to the client
        with clientsLock:
            clients[self.key].extend(game_data.get_new())

        """
        main loop:
        - infinite loop
        - has timeout
        """
        # set the timeout from this time on
        self.client_socket.settimeout(0.001)

        # the main loop of the communication
        # this loop includes sending the massages from the server
        # and updating the server about the client actions
        while True:
            try:
                # send the massages from the server
                messages = []
                with clientsLock:
                    # not sure if needed
                    if self.key not in clients:
                        break

                    # if there is something that needs to be sent to the client, get it and delete it
                    if clients[self.key]:
                        messages = clients[self.key]
                        clients[self.key] = []

                # send everything to the client
                for message in messages:
                    protocol.send_data(self.client_socket, message)

                # not sure if try needed
                # probably needed for timeout
                try:
                    # get one message from the client
                    data = protocol.parse(protocol.recv_data(self.client_socket))

                    with dataLock:
                        # check the type of the massage and do action
                        # if the client changed his angle update the angle in the data
                        if data['type'] == protocol.Type.SNAKE and \
                                data['subtype'] == protocol.Subtype.SNAKE.change_angle:
                            # if as a protection
                            # the updates are sent all the time
                            # even when the client has not spawn yet
                            if self.key in game_data.snakes:
                                game_data.snakes[self.key].set_angle(data['angle'], ANGLE_LIM)

                        # if the client asked to spawn in the game
                        # make a new snake for him in a random location and with random angle
                        # then add it to the game
                        elif data['type'] == protocol.Type.GAME and \
                                data['subtype'] == protocol.Subtype.GAME.start:
                            # make new snake
                            snake = game.objects.PlayerSnake(game.objects.Point(random.randint(0, game_data.board.width),random.randint(0, game_data.board.height)), name)
                            # change it`s angle to be random
                            snake.angle = math.radians(random.randint(0, 360))
                            # add it to the game
                            # this includes sending updates to all the client
                            game_data.add_snake(self.key, snake)

                        # if the client is disconnection, get out
                        elif data['type'] == protocol.Type.DISCONNECTION and \
                                data['subtype'] == protocol.Subtype.DISCONNECTION.announce:
                            break

                except Exception:
                    # maybe should be continue
                    pass

            except socket.error:
                # if the client closed connection, stop
                break

        # close the communication with the client
        # clean all the variables and data of the client
        print 'Client Disconnected. address: {}'.format(self.client_addr)

        # delete the client from the client so it stops receiving messages
        with clientsLock:
            # delete the client
            del clients[self.key]

        # delete the client`s snake
        with dataLock:
            # the client snakes could be already gone when the client disconnects
            # (if the client was dead when he exited)
            # maybe the client snake should be set to None and not deleted when he dies
            if self.key in game_data.snakes:
                # delete the snake
                game_data.del_snake(self.key)

        # close the connection
        self.client_socket.close()


def main():
    # initialize the server socket
    print 'server started'
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', protocol.PORT))
    server_socket.listen(10)

    # set timeout
    server_socket.settimeout(0.001)

    # the main server loop
    # the main server threads gets new client and opens thread to them
    # and it makes most of the game calculations
    # like move the snakes, collision checks and more
    while True:
        print 'Cycles Per Second: {}'.format(clock.get_fps())

        try:
            # get new client
            # if got new client (didn't throw timeout exception)
            # open a new thread for it, and start the thread
            client_socket, client_addr = server_socket.accept()
            client_thread = ClientConnection(client_socket, client_addr)
            client_thread.start()

        except socket.timeout:
            # if got timeout, continue
            pass

        # lock the data so no new changes will be done
        with dataLock:
            # update the data, this includes all the calculations
            game_data.update()
            # get the updates in the format of protocol messages
            data = game_data.get_update()

            # send the updates to all the clients (only adds to their "mailbox")
            for client in clients.iterkeys():
                # add the messages
                clients[client].extend(data)
                # send end of data stream message
                clients[client].append(protocol.control_stream_end())

        # sleep
        # this is needed so the game wont run as fast as the server can
        # the server finish around 60 code cycles per second to support 60 fps.
        clock.tick(60)

    server_socket.close()


if __name__ == '__main__':
    main()
