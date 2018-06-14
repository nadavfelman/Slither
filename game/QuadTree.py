class Point(object):
    """

    """

    def __init__(self, x, y, data=None):
        """

        Args:
            x (int):
            y (int):
            data:
        """
        self.x = x
        self.y = y
        self.data = data

    def __str__(self):
        """

        Returns:
            str
        """
        return 'Point{{x: {}, y: {}}}'.format(self.x, self.y)

    def __repr__(self):
        """

        Returns:
            str
        """
        return self.__str__()


class Rect(object):
    """

    """

    def __init__(self, x, y, w, h):
        """

        Args:
            x (int):
            y (int):
            w (int):
            h (int):
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def collide(self, point):
        """

        Args:
            point (Point):

        Returns:
            bool
        """
        return self.x - self.w <= point.x < self.x + self.w and \
               self.y - self.h <= point.y < self.y + self.h

    def intersects(self, rect):
        """

        Args:
            rect (Rect):

        Returns:
            bool
        """
        return not (rect.x - rect.w > self.x + self.w or
                    rect.x + rect.w < self.x - self.w or
                    rect.y - rect.h > self.y + self.h or
                    rect.y + rect.h < self.y - self.h)


class QuadTree(object):
    """

    """

    def __init__(self, rect, capacity):
        """

        Args:
            rect (Rect):
            capacity (int):
        """

        self.rect = rect
        self.capacity = capacity
        self.points = []

        self.divided = False
        self.north_west_QT = None
        self.north_east_QT = None
        self.south_west_QT = None
        self.south_east_QT = None

    def insert(self, point):
        """

        Args:
            point (Point):

        Returns:
            bool
        """

        if not self.rect.collide(point):
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True
        else:
            if not self.divided:
                self.subdiv()

            if self.north_west_QT.insert(point):
                return True
            if self.north_east_QT.insert(point):
                return True
            if self.south_west_QT.insert(point):
                return True
            if self.south_east_QT.insert(point):
                return True
            return False

    def subdiv(self):
        """

        Returns:
            None
        """

        nw = Rect(self.rect.x - self.rect.w / 2, self.rect.y - self.rect.h / 2,
                  self.rect.w / 2, self.rect.h / 2)
        self.north_west_QT = QuadTree(nw, self.capacity)

        ne = Rect(self.rect.x + self.rect.w / 2, self.rect.y - self.rect.h / 2,
                  self.rect.w / 2, self.rect.h / 2)
        self.north_east_QT = QuadTree(ne, self.capacity)

        sw = Rect(self.rect.x - self.rect.w / 2, self.rect.y + self.rect.h / 2,
                  self.rect.w / 2, self.rect.h / 2)
        self.south_west_QT = QuadTree(sw, self.capacity)

        se = Rect(self.rect.x + self.rect.w / 2, self.rect.y + self.rect.h / 2,
                  self.rect.w / 2, self.rect.h / 2)
        self.south_east_QT = QuadTree(se, self.capacity)

        self.divided = True

    def qurey(self, rect):
        """

        Args:
            rect (Rect):

        Returns:
            list
        """

        found_points = []
        if self.rect.intersects(rect):
            found_points.extend(filter(lambda p: rect.collide(p), self.points))
            if self.divided:
                found_points.extend(self.north_west_QT.qurey(rect))
                found_points.extend(self.north_east_QT.qurey(rect))
                found_points.extend(self.south_west_QT.qurey(rect))
                found_points.extend(self.south_east_QT.qurey(rect))
        return found_points
