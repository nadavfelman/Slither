import objects
import protocol

class dataBase(object):
    """
    [summary]

    """

    def __init__(self):
        """
        [summary]
        """
        self.snakes = {}
        self.orbs = {}
        self.last_update = []
        self.width = 200
        self.height = 200

    def update(self):
        self.last_update = []
        self.move_snakes()

    def move_snakes(self):
        for id_, snake in self.snakes.iteritems():
            snake.move()
            self.last_update.append((id_, snake))

    def get_update(self):
        update = []
        for id_, obj in self.last_update:
            update.append(protocol.snake_full_update(id_, obj.head.location, [t.location for t in obj.tail]))
        return  update