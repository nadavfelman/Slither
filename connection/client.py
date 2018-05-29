import game
import protocol
import pygame
import socket
import threading
from math import atan2


class client_connection_out(threading.Thread):
    """[summary]

    Arguments:
        threading {[type]} -- [description]
    """

    def __init__(self, client_socket, storage):
        super(client_connection_out, self).__init__()
        self.client_socket = client_socket
        self.storage = storage

    def send_data(self, data):
        protocol.send_data(self.client_socket, data)

    def run(self):
        while True:
            for data in self.storage:
                self.send_data(data)

            del self.storage[:]


class client_connection_in(threading.Thread):
    """[summary]

    Arguments:
        threading {[type]} -- [description]
    """

    def __init__(self, client_socket, storage):
        super(client_connection_in, self).__init__()
        self.client_socket = client_socket
        self.storage = storage

    def receive_data(self):
        data = protocol.recv_data(self.client_socket)
        return data

    def run(self):
        while True:
            self.storage.append(self.receive_data())


class client_connection(object):
    """[summary]

    Arguments:
        object {[type]} -- [description]
    """

    def __init__(self, ip):
        self.data_received = []
        self.data_to_send = []

        sock = socket.socket()
        print ip, protocol.PORT
        sock.connect((ip, protocol.PORT))

        self.recv_thread = client_connection_in(sock, self.data_received)
        self.send_thread = client_connection_out(sock, self.data_to_send)

        self.recv_thread.start()
        self.send_thread.start()

    def end(self):
        self.recv_thread.exit = True
        self.send_thread.exit = True
    
    def send(self, data):
        self.data_to_send.append(data)
    
    def receive(self):
        return self.data_received.pop()
    
    def has_received(self):
        return len(self.data_received) != 0


class client(object):
    """[summary]

    Arguments:
        object {[type]} -- [description]
    """

    def __init__(self, ip, name):
        self.connection = client_connection(ip)
        self.snakes = {}
        self.orbs = {}
        self.board = None
        self.id_ = None

        while True:
            if self.connection.has_received():
                data = self.connection.receive()
                print data
                data = protocol.parse(data)
                if data['type'] == protocol.Type.INITIAL and data['subtype'] == protocol.Subtype.INITIAL.server:
                    self.board = None
                    self.id_ = data['id']
                    break

        self.connection.send(protocol.initial_client(name))

    def update(self):
        print 'update'
        self.update_angle()
        self.update_data()
    
    def update_angle(self):
        cx, cy = pygame.display.get_surface().get_size()
        cx, cy = cx / 2, cy / 2
        px, py = pygame.mouse.get_pos()
        dx = px - cx
        dy = py - cy
        angle = atan2(dy, dx)
        self.connection.send(protocol.snake_change_angle(angle))
    
    def update_data(self):
        datas = []
        if self.connection.has_received():
            while self.connection.has_received() and len(datas) < 100:
                datas.append(self.connection.receive())

        for data in datas:
            data = protocol.parse(data)
            print data
            if data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.new:
                print 'new'
                snake = game.objects.snake.create_snake(data['head'], data['name'], data['mass'],  data['tail'])
                self.snakes[data['id']] = snake
            elif data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.full_update:
                self.snakes[data['id']].update_snake((data['x'], data['y']), data['mass'], data['head'], data['tail'])
            elif data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.delete:
                del self.snakes[data['id']]
            elif data['type'] == protocol.Type.ORB and data['subtype'] == protocol.Subtype.ORB.new:
                orb = game.objects.orb(data['x'], data['y'], data['mass'], (25,178,2))
                self.orbs[data['id']] = orb
            elif data['type'] == protocol.Type.ORB and data['subtype'] == protocol.Subtype.ORB.delete:
                del self.orbs[data['id']]

    def render(self, surface):
        print 'render'
        surface.fill((0,0,0))

        for snake in self.snakes:
            snake.render(surface)

        for orb in self.orbs:
            orb.render(surface)
