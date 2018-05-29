"""
TODO:
    - complete filter in camera in render function.
    - complete snake_render
    - complete orb_render
"""

import pygame

import colors
import dataSets


class render(object):
    """
    [summary]  
    """

    DEFAULT_ZOOM = 1

    def __init__(self, display_rect, board_rect, dataBase):
        """[summary]

        Arguments:
            display_rect {[type]} -- [description]
            dataBase {dataSets.dataBase} -- [description]
        """
        self.display_rect = display_rect.copy()
        self.board_rect = board_rect.copy()
        self.dataBase = dataBase
        self.player_snake = None

        self.user_interface = user_interface(display_rect, board_rect)
        self.background_ = background(board_rect)

        self.camera_pos = (0, 0)
        self.camera_dim = (display_rect.width, display_rect.height)
        self.zoom = render.DEFAULT_ZOOM

    def set_camera_pos(self, pos):
        self.camera_pos = pos

    def set_camera_dimensions(self, dim):
        self.camera_dim = dim

    def set_player(self, player_snake):
        self.player_snake = player_snake
        self.user_interface.set_player(player_snake)

    def set_zoom(self, zoom):
        """

        zoom < 1 : zooming out, making everything smaller, more surface view.
        zoom > 1 : zooming in, making everything lager, less surface view.

        Arguments:
            scale {[type]} -- [description]
        """
        self.zoom = zoom

        width = self.display_rect.width / zoom
        height = self.display_rect.height / zoom
        self.set_camera_dimensions((width, height))

    def get_offsets(self):
        x, y = self.camera_pos
        xoff = (-x + self.camera_dim[0] / 2) * self.zoom
        yoff = (-y + self.camera_dim[1] / 2) * self.zoom
        return xoff, yoff

    def render(self, surface):
        self.render_background(surface)

        self.render_orbs(surface)
        self.render_snakes(surface)

        self.render_user_interface(surface)

    def render_background(self, surface):
        self.background_.render(surface, self.camera_pos,
                                self.camera_dim, self.zoom)

    def render_snakes(self, surface):
        xoff, yoff = self.get_offsets()

        snakes = self.dataBase.iter_snakes_objects()
        # filter(lambda s: self.camera_rect.colliderect(s.), snakes)
        in_camera_snakes = snakes
        for s in in_camera_snakes:
            render_snake(surface, s, self.zoom, xoff, yoff)

    def render_orbs(self, surface):
        xoff, yoff = self.get_offsets()

        orbs = self.dataBase.iter_orbs_objects()
        # filter(lambda o: self.camera_rect.colliderect(o.rect), orbs)
        in_camera_orbs = orbs
        for o in in_camera_orbs:
            render_orb(surface, o, self.zoom, xoff, yoff)

    def render_user_interface(self, surface):
        self.user_interface.render(surface)


class background(object):
    X_SPACING = 100
    Y_SPACING = 100
    LINE_THICKNESS = 1

    BACKGROUND_COLOR = colors.WARM_WHITE
    SECONDARY_COLOR = colors.GRAY126
    OUTZONE_COLOR = colors.LIGHT_PINK

    def __init__(self, board_rect, line_thickness=None, x_spacing=None, y_spacing=None):
        self.board_rect = board_rect  # board rect

        self.line_thickness = line_thickness or background.LINE_THICKNESS
        self.x_spacing = x_spacing or background.X_SPACING
        self.y_spacing = y_spacing or background.Y_SPACING

    def render(self, surface, camera_pos, camera_dim, scl):
        camera_x, camera_y = camera_pos
        camera_x, camera_y = camera_x * scl, camera_y * scl
        width, height = 1920, 1080

        surface.fill(background.OUTZONE_COLOR)

        x, y, width, height = (0, 0, 1920, 1080)
        rect = pygame.Rect(x, y, width, height)
        
        px = camera_x - width / 2
        if px < 0:
            rect.left += abs(px)
            rect.width -= abs(px)

        px = (self.board_rect.right * scl) - (camera_x + width / 2)
        if px < 0:
            rect.width -= abs(px)

        py = camera_y - height / 2
        if py < 0:
            rect.top += abs(py)
            rect.height -= abs(py)
        
        py = (self.board_rect.bottom * scl) - (camera_y + height / 2)
        if py < 0:
            rect.height -= abs(py)

        pygame.draw.rect(surface, background.BACKGROUND_COLOR, rect)


class user_interface(object):
    """
    [summary]
    """
    PLAYER_FONT_COLOR = colors.GRAY25
    PLAYER_FONT_SIZE = 30
    PLAYER_MIRGIN = 4

    def __init__(self, display_rect, board_rect):
        self.display_rect = display_rect
        self.board_rect = board_rect
        self.player_snake = None

    def render(self, surface):
        # self.render_leaderboard(surface)
        # self.render_minimap(surface)
        if self.player_snake:
            self.render_playerstats(surface)

    def set_player(self, player_snake):
        self.player_snake = player_snake

    def render_leaderboard(self, surface):
        raise NotImplementedError

    def render_playerstats(self, surface):
        size = user_interface.PLAYER_FONT_SIZE
        x = user_interface.PLAYER_MIRGIN
        y = self.display_rect.bottom - user_interface.PLAYER_MIRGIN - size
        message = 'your mass: {}'.format(self.player_snake.mass)
        color = user_interface.PLAYER_FONT_COLOR
        message_display(surface, message, x, y, size, color, False)

    def render_minimap(self, surface):
        raise NotImplementedError


def render_snake(surface, obj, scale=1, xoff=0, yoff=0):
    obj.render(surface, scale=scale, xoff=xoff, yoff=yoff)


def render_orb(surface, obj, scale=1, xoff=0, yoff=0):
    obj.render(surface, scale=scale, xoff=xoff, yoff=yoff)


def message_display(surface, text, x, y, size, color, center=True):
    font = pygame.font.Font('freesansbold.ttf', size)
    textSurface = font.render(text, True, color)
    TextRect = textSurface.get_rect()
    if center:
        TextRect.center = (x, y)
    else:
        TextRect.topleft = (x, y)
    surface.blit(textSurface, TextRect)
