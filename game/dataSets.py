import objects
import connection.protocol as protocol
import pygame
import random
import  QuadTree


class ServerDataBase(object):
    """
    [summary]

    """

    ORB_LIMIT = 350

    def __init__(self):
        """
        [summary]
        """
        self.snakes = {}
        self.orbs = {}

        self.board = pygame.Rect(0, 0, 2000, 2000)

        self.last_update = []
        self.control = []

    def add_snake(self, id_, snake):
        self.snakes[id_] = snake
        data = protocol.snake_new(id_, snake.name, snake.mass, snake.head.point.pos, [t.point.pos for t in snake.tail])
        self.control.append(data)

    def del_snake(self, id_):
        del self.snakes[id_]
        data = protocol.snake_delete(id_)
        self.control.append(data)

    def add_orb(self, id_, orb):
        self.orbs[id_] = orb
        data = protocol.orb_new(id_, orb.mass, orb.point.x, orb.point.y, orb.color)
        self.control.append(data)

    def del_orb(self, id_):
        del self.orbs[id_]
        data = protocol.orb_delete(id_)
        self.control.append(data)

    def snake_drop(self, snake):
        value = snake.mass / snake.length
        for section in snake.tail + [snake.head]:
            point = section.point.copy()
            point.x += random.randint(0, 12)
            point.y += random.randint(0, 12)
            orb = objects.Orb(point, value)
            key = protocol.key(orb)
            self.add_orb(key, orb)

    def update(self):
        self.last_update = []
        quad_tree = QuadTree.QuadTree(QuadTree.Rect(self.board.centerx, self.board.centery, self.board.width / 2, self.board.height / 2), 5)
        for key, orb in self.orbs.iteritems():
            quad_tree.insert(QuadTree.Point(orb.point.x, orb.point.y, key))

        self.move_snakes()
        self.orbs_collision(quad_tree)
        self.snakes_collision()
        self.border_collision()
        self.add_orbs()

    def move_snakes(self):
        for id_, snake in self.snakes.iteritems():
            snake.move()
            data = protocol.snake_full_update(id_, snake.mass, snake.head.point.pos, [t.point.pos for t in snake.tail])
            self.last_update.append(data)

    def orbs_collision(self, quad_tree):
        for snake in self.snakes.itervalues():
            for sector in [snake.head] + snake.tail:
                range = QuadTree.Rect(sector.point.x, sector.point.y, sector.radius + objects.Orb.MAX_RADIUS, sector.radius + objects.Orb.MAX_RADIUS)
                orbs = quad_tree.qurey(range)
                for orb_point in orbs:
                    key = orb_point.data
                    if key not in self.orbs:
                        continue

                    orb = self.orbs[key]
                    if sector.intersects(orb):
                        self.del_orb(key)
                        snake.mass += orb.mass

    def snakes_collision(self):
        for key, snake in self.snakes.items():
            for other_key, other_snake in self.snakes.items():
                if key != other_key:
                    if other_snake.any_collide(snake.head):
                        self.del_snake(key)
                        self.snake_drop(snake)

    def border_collision(self):
        for key, snake in self.snakes.items():
            if snake.boarders_collide(self.board):
                self.del_snake(key)
                self.snake_drop(snake)

    def add_orbs(self):
        while len(self.orbs) < ServerDataBase.ORB_LIMIT:
            x = random.randint(0, self.board.width)
            y = random.randint(0, self.board.height)
            orb = objects.Orb(objects.Point(x, y))
            id_ = protocol.key(orb)
            self.add_orb(id_, orb)

    def get_update(self):
        last_update = self.control + self.last_update
        self.control = []
        return last_update

    def get_new(self):
        update = []
        for id_, snake in self.snakes.iteritems():
            data = protocol.snake_new(id_, snake.name, snake.mass, snake.head.point.pos, [t.point.pos for t in snake.tail])
            update.append(data)
        for id_, orb in self.orbs.iteritems():
            data = protocol.orb_new(id_, orb.mass, orb.point.x, orb.point.y, orb.color)
            update.append(data)
        return update
