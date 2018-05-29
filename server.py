import socket
import threading
import connection.protocol as protocol
import game
import pygame

clients = {}
clientsLock = threading.Lock()
game_data = game.dataSets.dataBase()
dataLock = threading.Lock()
clock = pygame.time.Clock()


class client_connection(threading.Thread):
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

        super(client_connection, self).__init__(name='CCThread-{}'.format(client_addr[0]))
        self.client_addr = client_addr
        self.client_socket = client_socket
        self.key = protocol.key(self.client_socket)

    def run(self):
        """
        [summary]
        """

        global clients
        global clientsLock
        global game_data

        with clientsLock:
            clients[self.key] = []

        protocol.send_data(self.client_socket, protocol.initial_server(game_data.width, game_data.height, self.key))

        while True:
            try:
                data = protocol.recv_data(self.client_socket)
                data = protocol.parse(data)
                if data['type'] == protocol.Type.INITIAL and data['subtype'] == protocol.Subtype.INITIAL.client:
                    name = data['name']
                    break
            except Exception:
                pass

        with dataLock:
            game_data.snakes[self.key] = game.objects.playerSnake((100, 100), name)
        with clientsLock:
            snake = game_data.snakes[self.key]
            head = snake.head.location
            tail = [t.location for t in snake.tail]
            clients[self.key].append(protocol.snake_new(self.key, snake.name, snake.mass, head, tail))

        while True:
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
                        game_data.snakes[self.key].set_angle(data['angle'])
            except Exception:
                pass

        with clientsLock:
            del clients[self.key]

def main():
    global game_data
    global dataLock
    global clients

    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', protocol.PORT))
    server_socket.listen(10)
    server_socket.settimeout(0.001)
    print 'started'

    while True:
        try:
            client_socket, client_addr = server_socket.accept()
            client_thread = client_connection(client_socket, client_addr)
            client_thread.start()
            print 'new client'
        except socket.timeout as e:
            pass

        with dataLock:
            game_data.update()
            data = game_data.get_update()


            for client in clients.iterkeys():
                clients[client].extend(data)
                clients[client].append(protocol.control_stream_end())

        clock.tick(60)


if __name__ == '__main__':
    main()
