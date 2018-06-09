import socket
import threading
import connection.protocol as protocol
import game
import pygame
import math
import random

ANGLE_LIM = math.pi * 0.04

clients = {}
clientsLock = threading.Lock()
game_data = game.dataSets.ServerDataBase()
dataLock = threading.Lock()
clock = pygame.time.Clock()


class ClientConnection(threading.Thread):
    """
    [summary]
    """

    def __init__(self, client_socket, client_addr):
        """
        [summary]

        Arguments:
            client_socket {[type]} -- [description]
            client_addr {[type]} -- [description]
        """

        super(ClientConnection, self).__init__()
        self.client_addr = client_addr
        self.client_socket = client_socket
        self.key = protocol.key(self.client_socket)

    def run(self):
        """
        [summary]
        """
        with clientsLock:
            clients[self.key] = []

        protocol.send_data(self.client_socket, protocol.initial_server(game_data.board.width, game_data.board.height, self.key))

        while True:
            try:
                data = protocol.recv_data(self.client_socket)
                data = protocol.parse(data)
                if data['type'] == protocol.Type.INITIAL and data['subtype'] == protocol.Subtype.INITIAL.client:
                    name = data['name']
                    break
            except Exception:
                pass

        with clientsLock:
            clients[self.key].extend(game_data.get_new())

        while True:
            try:
                messages = []
                with clientsLock:
                    if self.key not in clients:
                        break
                    if clients[self.key]:
                        messages = clients[self.key]
                        clients[self.key] = []
                for message in messages:
                    protocol.send_data(self.client_socket, message)

                try:
                    data = protocol.parse(protocol.recv_data(self.client_socket))
                    with dataLock:
                        if data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.change_angle:
                            if self.key in game_data.snakes:
                                game_data.snakes[self.key].set_angle(data['angle'], ANGLE_LIM)
                        elif data['type'] == protocol.Type.GAME and data['subtype'] == protocol.Subtype.GAME.start:
                            snake = game.objects.PlayerSnake(game.objects.Point(random.randint(0, game_data.board.width), random.randint(0, game_data.board.height)), name)
                            game_data.add_snake(self.key, snake)
                        elif data['type'] == protocol.Type.DISCONNECTION and data['subtype'] == protocol.Subtype.DISCONNECTION.announce:
                            break
                except Exception:
                    pass
            except socket.error as e:
                break

        with clientsLock:
            del clients[self.key]
        with dataLock:
            if self.key in game_data.snakes:
                game_data.del_snake(self.key)
        self.client_socket.close()


def main():
    print 'server started'
    server_socket = socket.socket()
    # server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', protocol.PORT))
    server_socket.listen(10)
    server_socket.settimeout(0.001)

    while True:
        print 'Cycles Per Second: {}'.format(clock.get_fps())
        try:
            client_socket, client_addr = server_socket.accept()
            print 'New Client Connected. address: {}'.format(client_addr)
            client_thread = ClientConnection(client_socket, client_addr)
            client_thread.start()
        except socket.timeout:
            pass

        with dataLock:
            game_data.update()
            data = game_data.get_update()

            for client in clients.iterkeys():
                clients[client].extend(data)
                clients[client].append(protocol.control_stream_end())

        clock.tick(60)

    server_socket.close()


if __name__ == '__main__':
    main()
