import socket
from math import atan2

import pygame

import game
import protocol


class Client(object):
    """
    [summary]
    """

    def __init__(self, ip, name):
        """

        Args:
            ip (str): valid ip of the server.
            name (str): the name of the player.
        """
        # variables declaration
        self.sock = socket.socket()
        self.key = None

        self.snakes = {}
        self.orbs = {}

        self.display = pygame.display.get_surface().get_rect()
        self.board = None
        self.render_control = None

        # initial connection
        self.sock.connect((ip, protocol.PORT))
        self.sock.settimeout(None)

        # get server initial
        while True:
            data = protocol.parse(protocol.recv_data(self.sock))
            if data['type'] == protocol.Type.INITIAL and \
                    data['subtype'] == protocol.Subtype.INITIAL.server:
                self.board = pygame.Rect(0, 0, data['width'], data['height'])
                self.key = data['id']
                break
        self.render_control = game.render.Render(self.display, self.board, self.snakes, self.orbs)

        # send client initial
        protocol.send_data(self.sock, protocol.initial_client(name))

        # end init function and add timeout
        self.sock.settimeout(0.001)

    def update(self):
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
        count = 0
        while True:
            try:
                data = protocol.recv_data(self.sock)
            except socket.timeout:
                break

            data = protocol.parse(data)
            if data['type'] == protocol.Type.CONTROL and \
                    data['subtype'] == protocol.Subtype.CONTROL.stream_end:
                if count == 0:
                    count += 1
                else:
                    break

            elif data['type'] == protocol.Type.SNAKE and \
                    data['subtype'] == protocol.Subtype.SNAKE.new:
                snake = game.objects.Snake.create_snake(game.objects.Point(*data['head']), data['name'], data['mass'],
                                                        data['tail'])
                self.snakes[data['id']] = snake
                if self.key == data['id']:
                    self.render_control.player = snake

            elif data['type'] == protocol.Type.SNAKE and \
                    data['subtype'] == protocol.Subtype.SNAKE.full_update:
                if not data['id'] in self.snakes:
                    continue
                self.snakes[data['id']].update_snake(data['mass'], data['head'], data['tail'])

            elif data['type'] == protocol.Type.SNAKE and \
                    data['subtype'] == protocol.Subtype.SNAKE.delete:
                del self.snakes[data['id']]

            elif data['type'] == protocol.Type.ORB and \
                    data['subtype'] == protocol.Subtype.ORB.new:
                orb = game.objects.Orb(game.objects.Point(data['x'], data['y']), data['mass'], data['color'])
                self.orbs[data['id']] = orb

            elif data['type'] == protocol.Type.ORB and \
                    data['subtype'] == protocol.Subtype.ORB.delete:
                del self.orbs[data['id']]

    def render(self, surface):
        self.render_control.render(surface)

    def close(self):
        protocol.send_data(self.sock, protocol.disconnection_announce())
        self.sock.close()

    def get_player(self):
        if self.key and self.key in self.snakes:
            return self.snakes[self.key]

    def start_game(self):
        protocol.send_data(self.sock, protocol.game_start())
