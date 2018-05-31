import objects
import connection.protocol as protocol


class DataBase(object):
    """
    [summary]

    """

    def __init__(self):
        """
        [summary]
        """
        self.snakes = {}
        self.orbs = {}

        self.width = 3000
        self.height = 3000

        self.last_update = []
        self.control = []

    def update(self):
        self.last_update = []
        self.move_snakes()

    def move_snakes(self):
        for id_, snake in self.snakes.iteritems():
            snake.move()
            data = protocol.snake_full_update(id_, snake.mass, snake.head.location, [t.location for t in snake.tail])
            self.last_update.append(data)

    def add_snake(self, id_, snake):
        self.snakes[id_] = snake
        data = protocol.snake_new(id_, snake.name, snake.mass, snake.head.location, [t.location for t in snake.tail])
        self.control.append(data)

    def del_snake(self, id_):
        del self.snakes[id_]
        data = protocol.snake_delete(id_)
        self.control.append(data)

    def get_update(self):
        last_update = self.control + self.last_update
        self.control = []
        return last_update

    def get_new(self):
        update = []
        for id_, obj in self.snakes.iteritems():
            data = protocol.snake_new(id_, obj.name, obj.mass, obj.head.location, [t.location for t in obj.tail])
            update.append(data)
        return update
