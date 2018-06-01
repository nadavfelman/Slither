import objects
import connection.protocol as protocol
import pygame
import random


class ServerDataBase(object):
    """
    [summary]

    """

    ORB_LIMIT = 50

    def __init__(self):
        """
        [summary]
        """
        self.snakes = {}
        self.orbs = {}
        self.orbs_collision_group = pygame.sprite.Group()

        self.width = 3000
        self.height = 3000

        self.last_update = []
        self.control = []

    def add_snake(self, id_, snake):
        self.snakes[id_] = snake
        data = protocol.snake_new(id_, snake.name, snake.mass, snake.head.location, [t.location for t in snake.tail])
        self.control.append(data)

    def del_snake(self, id_):
        del self.snakes[id_]
        data = protocol.snake_delete(id_)
        self.control.append(data)

    def add_orb(self, id_, orb):
        self.orbs[id_] = orb
        self.orbs_collision_group.add(orb)
        data = protocol.orb_new(id_, orb.mass, orb.x, orb.y)
        self.control.append(data)

    def del_orb(self, id_):
        del self.orbs[id_]
        data = protocol.orb_delete(id_)
        self.control.append(data)

    def update(self):
        self.last_update = []
        self.move_snakes()
        self.orbs_collision()
        self.snakes_collision()
        self.add_orbs()

    def move_snakes(self):
        for id_, snake in self.snakes.iteritems():
            snake.move()
            data = protocol.snake_full_update(id_, snake.mass, snake.head.location, [t.location for t in snake.tail])
            self.last_update.append(data)

    def orbs_collision(self):
        for snake in self.snakes.itervalues():
            for key, orb in self.orbs.items():
                if snake.any_collide(orb):
                    self.del_orb(key)
                    snake.add_mass(orb.mass)

    def snakes_collision(self):
        for key, snake in self.snakes.items():
            for other_key, other_snake in self.snakes.items():
                if key != other_key:
                    if other_snake.any_collide(snake.head):
                        self.del_snake(key)

    def add_orbs(self):
        while len(self.orbs) < ServerDataBase.ORB_LIMIT:
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            orb = objects.orb(x, y, 100, (152, 12, 58))
            id_ = protocol.key(orb)
            self.add_orb(id_, orb)

    def get_update(self):
        last_update = self.control + self.last_update
        self.control = []
        return last_update

    def get_new(self):
        update = []
        for id_, obj in self.snakes.iteritems():
            data = protocol.snake_new(id_, obj.name, obj.mass, obj.head.location, [t.location for t in obj.tail])
            update.append(data)
        for id_, obj in self.orbs.iteritems():
            data = protocol.orb_new(id_, obj.mass, obj.x, obj.y)
            update.append(data)
        return update
