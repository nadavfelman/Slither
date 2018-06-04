import math

import numpy as np
import pygame

import functions
import interface.colors as colors
import render


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return 'Point{{x: {}, y: {}}}'.format(self.x, self.y)

    def __repr__(self):
        return self.__str__()

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, pos):
        self.x, self.y = pos

    def copy(self):
        return Point(self.x, self.y)


class Circle(object):
    def __init__(self, point, radius):
        self.point = point
        self.radius = radius

    def __str__(self):
        return 'Circle{{x: {}, y: {}, radius: {}}}'.format(self.point.x, self.point.y, self.radius)

    def __repr__(self):
        return self.__str__()

    def collide(self, other):
        dx = self.point.x - other.point.x
        dy = self.point.y - other.point.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        return self.radius + other.radius >= distance


class Section(Circle):
    """
    [summary] 

    """

    def __init__(self, point, radius, angle=0):
        super(Section, self).__init__(point, radius)
        self.angle = angle

    @property
    def distance(self):
        return self.radius / 1.4

    def direct_to(self, point):
        self_x, self_y = self.point.pos
        loc_x, loc_y = point.pos
        dx = loc_x - self_x
        dy = loc_y - self_y
        self.angle = math.atan2(dy, dx)

    def next_location(self):
        next_point = self.point.copy()
        next_point.x += self.distance * math.cos(self.angle)
        next_point.y += self.distance * math.sin(self.angle)
        return next_point

    def move(self, distance):
        self.point.x += distance * math.cos(self.angle)
        self.point.y += distance * math.sin(self.angle)

    def relocate(self, point, max_move=None):
        # break out if already in place
        if self.next_location().pos == point.pos:
            return
        # change the angle so it will point at the new location
        self.direct_to(point)
        # check if the joint needs to be moved
        # if the head of the joint is on the location it does not need to be moved
        if self.next_location().pos != point.pos:
            # check if any max pixels moving distance was given.
            # if was given it checks whether the distance need to be moved is greater than the max moving distance.
            # if this returns true constrain the movement to the max moving distance else move regularly.
            # see attache number 0000.
            self_x, self_y = self.point.pos
            loc_x, loc_y = point.pos

            distance_to = math.sqrt(
                (self_x - loc_x) ** 2 + (self_y - loc_y) ** 2)

            if max_move and distance_to - self.distance > max_move:
                new_x = self_x + max_move * math.cos(self.angle)
                new_y = self_y + max_move * math.sin(self.angle)
                self.point.pos = (new_x, new_y)

            else:
                new_x = loc_x - self.distance * math.cos(self.angle)
                new_y = loc_y - self.distance * math.sin(self.angle)
                self.point.pos = (new_x, new_y)


class Snake(object):
    """
    [summary]
    """
    DEFAULT_MASS = 150
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

    def __init__(self, point, name):
        self.name = name
        self._mass = 0

        self.head = Section(point, self.radius)
        self.tail = []

        self.head_color = Snake.DEFAULT_HEAD_COLOR
        self.tail_color = Snake.DEFAULT_TAIL_COLOR

        self.mass = Snake.DEFAULT_MASS

    def __str__(self):
        return 'snake obj'

    def __repr__(self):
        return 'snake obj'

    @property
    def radius(self):
        return 10
        # return self.mass / 3000 + 10

    @property
    def distance(self):
        raise NotImplemented('distance should not be used in snake')
        # return self.mass / 4500 + 3

    @property
    def length(self):
        return self.mass / 100 + 10

    @property
    def location(self):
        return self.head.point.pos

    @property
    def angle(self):
        return self.head.angle

    @property
    def mass(self):
        return self._mass

    @mass.setter
    def mass(self, mass):
        self._mass = mass
        self.update_length()

    def update_length(self):
        length = int(round(self.length))
        dl = len(self.tail) - length

        if dl < 0:
            for _ in xrange(abs(dl)):
                if self.tail:
                    point = self.tail[-1].point.copy()
                else:
                    point = self.head.point.copy()

                new_sector = Section(point, self.radius)
                self.tail.append(new_sector)

        elif dl > 0:
            self.tail = self.tail[0: -abs(dl)]

    def relocate(self, point):
        self.head.relocate(point)
        previous_point = self.head.point
        for sector in self.tail:
            sector.relocate(previous_point)
            previous_point = sector.point

    def render(self, surface, scale=1, xoff=0, yoff=0):
        self.render_snake(surface, scale=scale, xoff=xoff, yoff=yoff)
        self.render_name(surface, scale=scale, xoff=xoff, yoff=yoff)

    def render_snake(self, surface, scale=1, xoff=0, yoff=0):
        # scale vector (for matrix or vector multiplication)
        scale_vector = np.array([[scale, 0], [0, scale]])
        # scaled radius of the circle
        scaled_radius = int(round(self.radius * scale))

        # draw trail
        # matrix of all the point in the trail
        matrix = np.array([sector.point.pos
                           for sector in self.tail[::-1]])
        # scaled matrix of the trail
        scaled_matrix = np.matmul(matrix, scale_vector)

        for x, y in scaled_matrix:
            # scaled x and y of one point with the offset applied
            offsetted_x = int(round(x + xoff))
            offsetted_y = int(round(y + yoff))
            pos = (offsetted_x, offsetted_y)  # position of the joint
            shadow_x = int(round(x + xoff + Snake.SHADOW_XOFF))
            shadow_y = int(round(y + yoff + Snake.SHADOW_YOFF))
            shadow_pos = (shadow_x, shadow_y)  # position of the shadow

            # draw the shadow of the joint
            pygame.draw.circle(surface, Snake.SHADOW_TAIL_COLOR,
                               shadow_pos, scaled_radius)
            pygame.draw.circle(surface, self.tail_color, pos,
                               scaled_radius)  # draw the joint

        # draw head
        # vector representing the location of head
        vector = np.array(self.head.point.pos)
        scaled_vector = vector.dot(scale_vector)  # scaled vector of head
        x, y = scaled_vector  # scaled x and y

        # scaled x and y with the offset applied
        offsetted_x = int(round(x + xoff))
        offsetted_y = int(round(y + yoff))
        pos = (offsetted_x, offsetted_y)  # position of the joint
        shadow_x = int(round(x + xoff + Snake.SHADOW_XOFF))
        shadow_y = int(round(y + yoff + Snake.SHADOW_YOFF))
        shadow_pos = (shadow_x, shadow_y)  # position of the shadow

        # draw the shadow of the joint
        pygame.draw.circle(surface, Snake.SHADOW_HEAD_COLOR,
                           shadow_pos, scaled_radius)
        pygame.draw.circle(surface, self.head_color,
                           pos, scaled_radius)  # draw the joint

    def render_name(self, surface, scale=1, xoff=0, yoff=0):
        size = Snake.NAME_FONT_SIZE
        color = Snake.NAME_FONT_COLOR

        x, y = self.location
        x = x * scale + xoff
        name_offset = self.radius * scale + size
        y = y * scale + yoff - name_offset

        render.message_display(surface, self.name, x, y, size, color)

    @staticmethod
    def create_snake(point, name, mass, tail):
        s = Snake(point, name)
        s.mass = mass
        for i, pos in enumerate(tail):
            s.tail[i].point.pos = pos
        return s

    def update_snake(self, mass, head, tail):
        self.head.point.pos = head
        self.mass = mass
        for i, pos in enumerate(tail):
            self.tail[i].point.pos = pos


class PlayerSnake(Snake):
    """
    [summary] 
    """

    REGULAR_SPEED = 2
    BOOST_SPEED = 5

    def __init__(self, location, name):
        super(PlayerSnake, self).__init__(location, name)

        self.regular_speed = PlayerSnake.REGULAR_SPEED
        self.boost_speed = PlayerSnake.BOOST_SPEED
        self.current_speed = self.regular_speed

    def move(self):
        self.head.move(self.current_speed)
        previous_point = self.head.point
        for sector in self.tail:
            sector.relocate(previous_point)
            previous_point = sector.point

    def set_angle(self, angle, limit=None):
        if limit:
            if abs(self.angle - angle) > math.pi:
                dir_control = -1
            else:
                dir_control = 1

            if self.angle < angle:
                new_angle = self.angle + limit * dir_control
                new_angle += math.pi
                new_angle %= 2 * math.pi
                new_angle -= math.pi
                self.head.angle = new_angle
            else:
                new_angle = self.angle - limit * dir_control
                new_angle += math.pi
                new_angle %= 2 * math.pi
                new_angle -= math.pi
                self.head.angle = new_angle
        else:
            self.head.angle = angle

    def direct_to(self, point):
        self.head.direct_to(point)

    def tail_collide(self, circle):
        for t in self.tail:
            if t.collide(circle):
                return True

    def head_collide(self, circle):
        return self.head.collide(circle)

    def any_collide(self, circle):
        return self.tail_collide(circle) or self.head_collide(circle)

    def boarders_collide(self, board_rect):
        if any([t.point.y - t.radius < board_rect.top for t in self.tail]):
            return True
        elif any([t.point.y + t.radius > board_rect.bottom for t in self.tail]):
            return True
        elif any([t.point.x - t.radius < board_rect.left for t in self.tail]):
            return True
        elif any([t.point.x + t.radius > board_rect.right for t in self.tail]):
            return True
        return False


class Orb(Circle):
    """
    [summary]
    """

    MIN_MASS = 20
    MAX_MASS = 150

    MIN_RADIUS = 2
    MAX_RADIUS = 8

    ORB_COLORS = [
        colors.RED,
        colors.PURPLE,
        colors.ORANGE,
        colors.PINK_SLIME,
        colors.LIGHT_ARMY_GREEN
    ]

    def __init__(self, center, mass, color):
        """
        [summary]

        Arguments:
            x {[type]} -- [description]
            y {[type]} -- [description]
            mass {[type]} -- [description]
            color {[type]} -- [description]
        """

        radius = int(round(functions.map_range(
            mass, (Orb.MIN_MASS, Orb.MAX_MASS), (Orb.MIN_RADIUS, Orb.MAX_RADIUS))))

        super(Orb, self).__init__(center, radius)

        self.mass = mass
        self.color = color

    def render(self, surface, scale=1, xoff=0, yoff=0):
        location_vector = np.array(self.point.pos)
        scale_vector = np.array([[scale, 0], [0, scale]])

        scaled_vector = location_vector.dot(scale_vector)
        x, y = scaled_vector

        offsetted_x = int(round(x + xoff))
        offsetted_y = int(round(y + yoff))
        pos = (offsetted_x, offsetted_y)

        radius = int(round(self.radius * scale))

        pygame.draw.circle(surface, self.color, pos, radius)
