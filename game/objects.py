import math

import numpy as np
import pygame

import interface.colors as colors
import functions
import render


class section(pygame.sprite.Sprite):
    """
    [summary] 

    """

    def __init__(self, location, distance, radius, angle=0):
        super(section, self).__init__()

        self._location = location
        self.distance = distance
        self.radius = radius
        self.angle = angle

    @property
    def rect(self):
        diameter = 2 * self.radius
        rect = pygame.Rect(0, 0, diameter, diameter)
        rect.center = self.location
        return rect

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, location):
        # self._location = map(lambda x: round(x, 0), location)
        self._location = location

    def direct_to(self, location):
        self_x, self_y = self.location
        loc_x, loc_y = location

        dx = loc_x - self_x
        dy = loc_y - self_y
        self.angle = math.atan2(dy, dx)

    def next_location(self):
        self_x, self_y = self.location
        next_x = self_x + self.distance * math.cos(self.angle)
        next_y = self_y + self.distance * math.sin(self.angle)
        return (next_x, next_y)

    def relocate(self, location, max_move=None):
        # break out if already in place
        if self.next_location() == location:
            return

        # change the angle so it will point at the new location
        self.direct_to(location)

        # check if the joint needs to be moved
        # if the head of the joint is on the location it does not need to be moved
        if self.next_location() != location:
            # check if any max pixels moving distance was given.
            # if was given it checks whether the distance need to be moved is greater than the max moving distance.
            # if this returns true constrain the movement to the max moving distance else move regularly.
            # see attache number 0000.
            self_x, self_y = self.location
            loc_x, loc_y = location

            distance_to = math.sqrt(
                (self_x - loc_x) ** 2 + (self_y - loc_y) ** 2)

            if max_move and distance_to - self.distance > max_move:
                new_x = self_x + max_move * math.cos(self.angle)
                new_y = self_y + max_move * math.sin(self.angle)
                self.location = (new_x, new_y)

            else:
                new_x = loc_x - self.distance * math.cos(self.angle)
                new_y = loc_y - self.distance * math.sin(self.angle)
                self.location = (new_x, new_y)

    def move(self, move_amount):
        x, y = self.location
        new_x = x + move_amount * math.cos(self.angle)
        new_y = y + move_amount * math.sin(self.angle)
        self.location = (new_x, new_y)


class snake(object):
    """
    [summary]
    """
    DEFAULT_MASS = 10
    DEFAULT_HEAD_COLOR = colors.RED
    DEFAULT_TAIL_COLOR = colors.GRAY66

    # name variables
    NAME_FONT_SIZE = 20
    NAME_FONT_COLOR = colors.GRAY25

    # render variables
    SHADOW_XOFF = 1
    SHADOW_YOFF = 1
    SHADOW_HEAD_COLOR = colors.DARK_RED
    SHADOW_TAIL_COLOR = colors.GRAY126

    def __init__(self, location, name):
        self.name = name
        self.mass = snake.DEFAULT_MASS

        self.head_color = snake.DEFAULT_HEAD_COLOR
        self.tail_color = snake.DEFAULT_TAIL_COLOR

        self.head = section(location, self.get_distance(), self.get_radius())
        self.tail = []

        self.update_mass()

    def __str__(self):
        return 'snake obj'

    def __repr__(self):
        return 'snake obj'

    def get_radius(self):
        return self.mass / 3000 + 4

    def get_distance(self):
        return self.mass / 4500 + 3

    def get_length(self):
        return self.mass / 150 + 10

    def get_location(self):
        return self.head.location

    def get_angle(self):
        return self.head.angle

    def update_length(self):
        length = int(round(self.get_length()))
        dl = len(self.tail) - length

        if dl < 0:
            for _ in xrange(abs(dl)):
                if self.tail:
                    loc = self.tail[-1].location
                else:
                    loc = self.head.location

                new_sector = section(
                    loc, self.get_distance(), self.get_radius())
                self.tail.append(new_sector)
        elif dl > 0:
            self.tail = self.tail[0: -abs(dl)]

    def update_distance(self):
        new_distance = self.get_distance()
        self.head.distance = new_distance
        for j in self.tail:
            j.distance = new_distance

    def update_radius(self):
        new_radius = self.get_radius()
        self.head.distance = new_radius
        for j in self.tail:
            j.distance = new_radius

    def update_mass(self):
        self.update_length()
        self.update_radius()
        self.update_distance()

    def add_mass(self, amount):
        self.mass += amount
        self.update_mass()

    def sub_mass(self, amount):
        self.mass -= amount
        self.update_mass()

    def relocate(self, location):
        self.head.relocate(location)
        previous_location = self.head.location
        for sector in self.tail:
            sector.relocate(previous_location)
            previous_location = sector.location

    def render(self, surface, scale=1, xoff=0, yoff=0):
        self.render_snake(surface, scale=scale, xoff=xoff, yoff=yoff)
        self.render_name(surface, scale=scale, xoff=xoff, yoff=yoff)

    def render_snake(self, surface, scale=1, xoff=0, yoff=0):
        # scale vector (for matrix or vector multiplication)
        scale_vector = np.array([[scale, 0], [0, scale]])
        # scaled radius of the circle
        scaled_radius = int(round(self.get_radius() * scale))

        # draw trail
        # matrix of all the point in the trail
        matrix = np.array([sector.location
                           for sector in self.tail[::-1]])
        # scaled matrix of the trail
        scaled_matrix = np.matmul(matrix, scale_vector)

        for x, y in scaled_matrix:
            # scaled x and y of one point with the offset applied
            offsetted_x = int(round(x + xoff))
            offsetted_y = int(round(y + yoff))
            pos = (offsetted_x, offsetted_y)  # position of the joint
            shadow_x = int(round(x + xoff + snake.SHADOW_XOFF))
            shadow_y = int(round(y + yoff + snake.SHADOW_YOFF))
            shadow_pos = (shadow_x, shadow_y)  # position of the shadow

            # draw the shadow of the joint
            pygame.draw.circle(surface, snake.SHADOW_TAIL_COLOR,
                               shadow_pos, scaled_radius)
            pygame.draw.circle(surface, self.tail_color, pos,
                               scaled_radius)  # draw the joint

        # draw head
        # vector representing the location of head
        vector = np.array(self.head.location)
        scaled_vector = vector.dot(scale_vector)  # scaled vector of head
        x, y = scaled_vector  # scaled x and y

        # scaled x and y with the offset applied
        offsetted_x = int(round(x + xoff))
        offsetted_y = int(round(y + yoff))
        pos = (offsetted_x, offsetted_y)  # position of the joint
        shadow_x = int(round(x + xoff + snake.SHADOW_XOFF))
        shadow_y = int(round(y + yoff + snake.SHADOW_YOFF))
        shadow_pos = (shadow_x, shadow_y)  # position of the shadow

        # draw the shadow of the joint
        pygame.draw.circle(surface, snake.SHADOW_HEAD_COLOR,
                           shadow_pos, scaled_radius)
        pygame.draw.circle(surface, self.head_color,
                           pos, scaled_radius)  # draw the joint

    def render_name(self, surface, scale=1, xoff=0, yoff=0):
        size = snake.NAME_FONT_SIZE
        color = snake.NAME_FONT_COLOR

        x, y = self.get_location()
        x = x * scale + xoff
        name_offset = self.get_radius() * scale + size
        y = y * scale + yoff - name_offset

        render.message_display(surface, self.name, x, y, size, color)

    @staticmethod
    def create_snake(loc, name, mass, tail):
        s = snake(loc, name)
        s.mass = mass
        s.update_mass()
        for i, pos in enumerate(tail):
            s.tail[i].location = pos
        return s

    def update_snake(self, mass, head, tail):
        self.head.location = head
        self.mass = mass
        self.update_mass()
        for i, pos in enumerate(tail):
            self.tail[i].location = pos


class playerSnake(snake):
    """
    [summary] 
    """

    REGULAR_SPEED = 0.7
    BOOST_SPEED = 5

    MAX_ANGLE_CHANGE = math.radians(3)

    def __init__(self, location, name):
        super(playerSnake, self).__init__(location, name)

        self.regular_speed = playerSnake.REGULAR_SPEED
        self.boost_speed = playerSnake.BOOST_SPEED
        self.current_speed = self.regular_speed

    def move(self):
        self.head.move(self.current_speed)
        pre_location = self.head.location
        for sector in self.tail:
            sector.relocate(pre_location)
            pre_location = sector.location

    def set_angle(self, angle, limit=None):
        if limit:
            if abs(self.get_angle() - angle) > math.pi:
                dir_control = -1
            else:
                dir_control = 1

            if self.get_angle() < angle:
                new_angle = self.get_angle() + limit * dir_control
                new_angle += math.pi
                new_angle %= 2 * math.pi
                new_angle -= math.pi
                self.head.angle = new_angle
            else:
                new_angle = self.get_angle() - limit * dir_control
                new_angle += math.pi
                new_angle %= 2 * math.pi
                new_angle -= math.pi
                self.head.angle = new_angle
        else:
            self.head.angle = angle

    def direct_to(self, location):
        self_x, self_y = self.get_location()
        loc_x, loc_y = location

        dx = loc_x - self_x
        dy = loc_y - self_y
        self.set_angle(math.atan2(dy, dx))

    def tail_collide(self, sprite_obj):
        return any([pygame.sprite.collide_circle(sprite_obj, t) for t in self.tail])

    def head_collide(self, sprite_obj):
        return pygame.sprite.collide_circle(sprite_obj, self.head)

    def any_collide(self, sprite_obj):
        return self.head_collide(sprite_obj) or self.tail_collide(sprite_obj)

    def boarders_collide(self, board_rect):
        if any([s.location[1] - s.radius < board_rect.top for s in self.tail]):
            return True
        elif any([s.location[1] + s.radius > board_rect.bottom for s in self.tail]):
            return True
        elif any([s.location[0] - s.radius < board_rect.left for s in self.tail]):
            return True
        elif any([s.location[0] + s.radius > board_rect.right for s in self.tail]):
            return True
        return False


class orb(pygame.sprite.Sprite):
    """
    [summary]
    """

    MIN_MASS = 10
    MAX_MASS = 100

    MIN_RADIUS = 2
    MAX_RADIUS = 12

    ORB_COLORS = [
        colors.RED,
        colors.PURPLE,
        colors.ORANGE,
        colors.PINK_SLIME,
        colors.LIGHT_ARMY_GREEN
    ]

    def __init__(self, x, y, mass, color):
        """
        [summary]

        Arguments:
            x {[type]} -- [description]
            y {[type]} -- [description]
            mass {[type]} -- [description]
            color {[type]} -- [description]
        """

        super(orb, self).__init__()

        self.mass = mass
        self.x = x
        self.y = y
        self.radius = int(round(functions.map_range(
            mass, (orb.MIN_MASS, orb.MAX_MASS), (orb.MIN_RADIUS, orb.MAX_RADIUS))))

        diameter = 2 * self.radius
        self.rect = pygame.Rect(0, 0, diameter, diameter)
        self.rect.center = (x, y)

        self.color = color

    def get_location(self):
        return self.rect.center

    def render(self, surface, scale=1, xoff=0, yoff=0):
        location_vector = np.array(self.get_location())
        scale_vector = np.array([[scale, 0], [0, scale]])

        scaled_vector = location_vector.dot(scale_vector)
        x, y = scaled_vector

        offsetted_x = int(round(x + xoff))
        offsetted_y = int(round(y + yoff))
        pos = (offsetted_x, offsetted_y)

        radius = int(round(self.radius * scale))

        pygame.draw.circle(surface, self.color, pos, radius)
