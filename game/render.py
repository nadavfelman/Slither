"""
TODO:
    - complete filter in camera in render function.
    - complete snake_render
    - complete orb_render
"""

import pygame
import interface.colors as colors


class render(object):
    """
    [summary]  
    """

    DEFAULT_ZOOM = 1

    def __init__(self, display_rect, board_rect, snakes, orbs):
        """[summary]

        Arguments:
            display_rect {[type]} -- [description]
            dataBase {dataSets.dataBase} -- [description]
        """
        self.display_rect = display_rect.copy()
        self.board_rect = board_rect.copy()
        self.camera_rect = display_rect.copy()
        self.snakes = snakes
        self.orbs = orbs
        self.player = None
        self.zoom = render.DEFAULT_ZOOM

    def set_zoom(self, zoom):
        self.zoom = zoom
        width = self.display_rect.width / zoom
        height = self.display_rect.height / zoom
        self.camera_rect.size = (width, height)

    def get_offsets(self):
        x, y = self.camera_rect.center
        xoff = (-x + self.display_rect.width / 2) * self.zoom
        yoff = (-y + self.display_rect.height / 2) * self.zoom
        return xoff, yoff

    def render(self, surface):
        if self.player:
            self.camera_rect.center = self.player.head.location
            self.set_zoom(self.display_rect.height * .03 / self.player.get_radius() + 1)

        xoff, yoff = self.get_offsets()
        self.render_orbs(surface, xoff, yoff)
        self.render_snakes(surface, xoff, yoff)

    def render_snakes(self, surface, xoff, yoff):
        snakes = self.snakes.itervalues()
        # filter(lambda s: self.camera_rect.colliderect(s.rec), snakes)
        in_camera_snakes = snakes
        for snake in in_camera_snakes:
            snake.render(surface, scale=self.zoom, xoff=xoff, yoff=yoff)

    def render_orbs(self, surface, xoff, yoff):
        orbs = self.orbs.itervalues()
        in_camera_orbs = orbs
        # in_camera_orbs = filter(lambda o: self.camera_rect.colliderect(o.rect), orbs)
        for orb in in_camera_orbs:
            orb.render(surface, scale=self.zoom, xoff=xoff, yoff=yoff)


def message_display(surface, text, x, y, size, color, center=True):
    font = pygame.font.Font('freesansbold.ttf', size)
    textSurface = font.render(text, True, color)
    TextRect = textSurface.get_rect()
    if center:
        TextRect.center = (x, y)
    else:
        TextRect.topleft = (x, y)
    surface.blit(textSurface, TextRect)