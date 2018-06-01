import game
import protocol
import pygame
import socket
from math import atan2
import interface.colors as colors


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
                self.board = pygame.Rect(0, 0, data['width'], data['height'])
                self.id_ = data['id']
                break

        protocol.send_data(self.sock, protocol.initial_client(name))
        self.sock.settimeout(0.01)

    def handle_event(self, event):
        pass
        if event.type == pygame.MOUSEMOTION:
            cx, cy = pygame.display.get_surface().get_rect().center
            px, py = event.pos
            dx = px - cx
            dy = py - cy
            angle = atan2(dy, dx)
            protocol.send_data(self.sock, protocol.snake_change_angle(angle))

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
        while True:
            try:
                data = protocol.recv_data(self.sock)
            except socket.timeout:
                break
            data = protocol.parse(data)
            if data['type'] == protocol.Type.CONTROL and data['subtype'] == protocol.Subtype.CONTROL.stream_end:
                break

            if data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.new:
                snake = game.objects.snake.create_snake(data['head'], data['name'], data['mass'], data['tail'])
                self.snakes[data['id']] = snake
            elif data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.full_update:
                if not data['id'] in self.snakes:
                    continue
                self.snakes[data['id']].update_snake(data['mass'], data['head'], data['tail'])
            elif data['type'] == protocol.Type.SNAKE and data['subtype'] == protocol.Subtype.SNAKE.delete:
                del self.snakes[data['id']]
            elif data['type'] == protocol.Type.ORB and data['subtype'] == protocol.Subtype.ORB.new:
                orb = game.objects.orb(data['x'], data['y'], data['mass'], (25, 178, 2))
                self.orbs[data['id']] = orb
            elif data['type'] == protocol.Type.ORB and data['subtype'] == protocol.Subtype.ORB.delete:
                del self.orbs[data['id']]

    def render(self, surface):
        surface.fill(colors.WARM_WHITE)

        zoom = 1
        xoff = 0
        yoff = 0
        x = 0
        y = 0

        if self.id_ in self.snakes:
            player = self.snakes[self.id_]
            # zoom = 1080 * .03 / player.get_radius() + 1
            width, height = 1920 / zoom, 1080 / zoom
            x, y = player.head.location
            xoff = (-x + width / 2) * zoom
            yoff = (-y + height / 2) * zoom

        for orb in self.orbs.itervalues():
            lx, ly = orb.x, orb.y
            dx, dy = x - lx, y - ly
            if (dx ** 2 + dy ** 2) ** 0.5 < 1920:
                orb.render(surface, zoom, xoff, yoff)

        for snake in self.snakes.itervalues():
            lx, ly = snake.head.location
            dx, dy = x - lx, y - ly
            if (dx ** 2 + dy ** 2) ** 0.5 < 1920:
                snake.render(surface, zoom, xoff, yoff)

    def close(self):
        protocol.send_data(self.sock, protocol.disconnection_announce())
        self.sock.close()
