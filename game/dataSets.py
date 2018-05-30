import objects
import connection.protocol as protocol

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
        # print 'data update'
        for id_, obj in self.last_update:
            data = protocol.snake_full_update(id_, obj.mass,obj.head.location, [t.location for t in obj.tail])
            # print 'up', ''.join([r'\x{:x}'.format(ord(c)) for c in data])
            update.append(data)
        return update

    def get_new(self):
        update = []
        # print 'data update'
        for id_, obj in self.last_update:
            data = protocol.snake_new(id_, obj.name, obj.mass, obj.head.location, [t.location for t in obj.tail])
            # print 'up', ''.join([r'\x{:x}'.format(ord(c)) for c in data])
            update.append(data)
        return update
