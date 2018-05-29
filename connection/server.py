import socket
import threading
import protocol
import game

clients = {}
cLock = threading.Lock()
game_data = game.dataSets.dataBase()
dLock = threading.Lock()


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
        global cLock
        global game_data

        with cLock:
            clients[self.key] = []

        protocol.send_data(self.client_socket, protocol.initial_server(game_data.width, game_data.height, self.key))

        while True:
            data = protocol.recv_data(self.client_socket)
            data = protocol.parse(data)
            if data['type'] == protocol.Type.INITIAL and data['subtype'] == protocol.Subtype.INITIAL.client:
                name = data['name']
                break

        with dLock:
            game_data.snakes[self.key] = game.objects.playerSnake((100, 100), name)
            print 's added'
        with cLock:
            snake = game_data.snakes[self.key]
            head = snake.head.location
            tail = [t.location for t in snake.tail]
            clients[self.key].append(protocol.snake_new(self.key, snake.name, snake.mass, head, tail))
            print 'cConn'

        ci = client_connection_in(self.client_socket, self.client_addr, self.key)
        co = client_connection_out(self.client_socket, self.client_addr, self.key)
        ci.start()
        co.start()
        ci.join()
        co.exit = True

        with cLock:
            del clients[self.key]


class client_connection_out(threading.Thread):
    """
    [summary]
    """

    def __init__(self, client_socket, client_addr, key):
        """
        [summary]

        Arguments:
            client_socket {[type]} -- [description]
            client_addr {[type]} -- [description]
        """

        super(client_connection_out, self).__init__(name='CCOThread-{}'.format(client_addr[0]))
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.key = key

    def run(self):
        """
        [summary]
        """

        global clients
        global cLock

        while True:
            messages = []

            with cLock:
                if self.key not in clients:
                    break

                if clients[self.key]:
                    messages = clients[self.key]
                    clients[self.key] = []

            for message in messages:
                protocol.send_data(self.client_socket, message)


class client_connection_in(threading.Thread):
    """
    [summary]
    """

    def __init__(self, client_socket, client_addr, key):
        """
        [summary]

        Arguments:
            client_socket {[type]} -- [description]
            client_addr {[type]} -- [description]
        """

        super(client_connection_in, self).__init__(name='CCIThread-{}'.format(client_addr[0]))
        self.client_socket = client_socket
        self.client_addr = client_addr
        self.key = key

    def run(self):
        """
        [summary]
        """

        global clients
        global cLock

        while True:
            data = protocol.parse(protocol.recv_data(self.client_socket))

            with dLock:
                if data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.change_angle:
                    game_data.snakes[self.key].set_angle(data['angle'])


def main():
    global game_data
    global dLock
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

        with dLock:
            game_data.update()
            data = game_data.get_update()
            # print game_data.snakes, data
            for client in clients.iterkeys():
                clients[client].extend(data)


if __name__ == '__main__':
    main()
