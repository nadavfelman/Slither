import pygame
import interface.colors as colors


class Rect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @property
    def center(self):
        return self.x + self.width / 2, self.y + self.height / 2

    @center.setter
    def center(self, center):
        center_x, center_y = center
        self.x = center_x - self.width / 2
        self.y = center_y - self.height / 2

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, size):
        self.width, self.height = size

    @property
    def bottom(self):
        return self.y + self.height

    @bottom.setter
    def bottom(self, bottom):
        self.y = bottom - self.height

    @property
    def right(self):
        return self.x + self.width

    @right.setter
    def right(self, right):
        self.y = right - self.width

    def __str__(self):
        return 'Rect{{x: {}, y: {}, width: {}, height: {}}}'.format(self.x, self.y, self.width, self.height)


class render(object):
    """
    [summary]  
    """

    def __init__(self, display_rect, board_rect, snakes, orbs):
        """[summary]

        Arguments:
            display_rect {[type]} -- [description]
            dataBase {dataSets.dataBase} -- [description]
        """
        self.display_rect = display_rect.copy()
        self.board_rect = board_rect.copy()
        self.camera_rect = Rect(display_rect.x, display_rect.y, display_rect.width, display_rect.height)
        self.snakes = snakes
        self.orbs = orbs
        self.player = None
        self.zoom = 1

    def set_zoom(self, zoom):
        self.zoom = zoom
        width = self.display_rect.width / zoom
        height = self.display_rect.height / zoom
        self.camera_rect.size = (width, height)

    def get_offsets(self):
        x, y = self.camera_rect.center
        xoff = (-x + self.display_rect.width / 2.0) * self.zoom
        yoff = (-y + self.display_rect.height / 2.0) * self.zoom
        return xoff, yoff

    def render(self, surface):
        if self.player:
            self.camera_rect.center = self.player.point.pos
            # self.set_zoom(self.display_rect.height * .03 / self.player.get_radius() + 1)

        xoff, yoff = self.get_offsets()
        self.render_background(surface, xoff, yoff)
        self.render_orbs(surface, xoff, yoff)
        self.render_snakes(surface, xoff, yoff)

    def render_snakes(self, surface, xoff, yoff):
        player_x, player_y = self.camera_rect.center
        for snake in self.snakes.itervalues():
            obj_x, obj_y = snake.head.point.pos
            dx, dy = player_x - obj_x, player_y - obj_y
            if (dx ** 2 + dy ** 2) ** 0.5 < self.display_rect.width:
                snake.render(surface, scale=self.zoom, xoff=xoff, yoff=yoff)

    def render_orbs(self, surface, xoff, yoff):
        player_x, player_y = self.camera_rect.center
        for orb in self.orbs.itervalues():
            obj_x, obj_y = orb.point.x, orb.point.y
            dx, dy = player_x - obj_x, player_y - obj_y
            if (dx ** 2 + dy ** 2) ** 0.5 < self.display_rect.width:
                orb.render(surface, scale=self.zoom, xoff=xoff, yoff=yoff)

    def render_background(self, surface, xoff, yoff):
        surface.fill(colors.RED)
        x = -self.camera_rect.x if self.camera_rect.x < 0 else 0
        y = -self.camera_rect.y if self.camera_rect.y < 0 else 0

        # width = round(min(self.display_rect.width - x, self.board_rect.height))
        # height = round(min(self.display_rect.height - y, self.board_rect.height))

        if self.camera_rect.right > self.board_rect.right:
            width = self.board_rect.right - self.camera_rect.x - x
        else:
            width = self.display_rect.width - x

        if self.camera_rect.bottom > self.board_rect.bottom:
            height = self.board_rect.bottom - self.camera_rect.y - y
        else:
            height = self.display_rect.height - y

        pygame.draw.rect(surface, colors.WARM_WHITE, (round(x), round(y), round(width), round(height)))


def message_display(surface, text, x, y, size, color, center=True):
    font = pygame.font.Font('freesansbold.ttf', size)
    textSurface = font.render(text, True, color)
    TextRect = textSurface.get_rect()
    if center:
        TextRect.center = (x, y)
    else:
        TextRect.topleft = (x, y)
    surface.blit(textSurface, TextRect)
