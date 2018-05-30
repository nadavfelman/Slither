import game
import protocol
import pygame
import socket
import threading
from math import atan2


class client(object):
    """[summary]

    Arguments:
        object {[type]} -- [description]
    """

    def __init__(self, ip, name):
        self.sock = socket.socket()
        self.snakes = {}
        self.orbs = {}
        self.board = None
        self.id_ = None

        self.sock.connect((ip, protocol.PORT))

        while True:
            data = protocol.parse(protocol.recv_data(self.sock))
            if data['type'] == protocol.Type.INITIAL and data['subtype'] == protocol.Subtype.INITIAL.server:
                self.board = None
                self.id_ = data['id']
                break

        protocol.send_data(self.sock, protocol.initial_client(name))
        self.sock.settimeout(0.01)

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
        protocol.send_data(self.sock, protocol.snake_change_angle(angle))

    def update_data(self):
        while True:
            try:
                data = protocol.recv_data(self.sock)
            except socket.timeout:
                break
            data = protocol.parse(data)
            # print data
            if data['type'] == protocol.Type.CONTROL and data['subtype'] == protocol.Subtype.CONTROL.stream_end:
                break

            if data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.new:
                # print 'new'
                snake = game.objects.snake.create_snake(data['head'], data['name'], data['mass'], data['tail'])
                self.snakes[data['id']] = snake
            elif data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.full_update:
                if not data['id'] in self.snakes:
                    continue
                # print 'mass', self.snakes[data['id']].mass, type(self.snakes[data['id']].mass)
                self.snakes[data['id']].update_snake(data['mass'], data['head'], data['tail'])
            elif data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.delete:
                del self.snakes[data['id']]
            elif data['type'] == protocol.Type.ORB and data['subtype'] == protocol.Subtype.ORB.new:
                orb = game.objects.orb(data['x'], data['y'], data['mass'], (25, 178, 2))
                self.orbs[data['id']] = orb
            elif data['type'] == protocol.Type.ORB and data['subtype'] == protocol.Subtype.ORB.delete:
                del self.orbs[data['id']]

    def render(self, surface):
        print 'render'
        surface.fill((0, 0, 0))

        for snake in self.snakes.itervalues():
            print snake.head.location
            snake.render(surface)

        for orb in self.orbs.itervalues():
            orb.render(surface)

    def close(self):
        self.sock.close()
