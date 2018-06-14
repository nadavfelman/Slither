import pygame
import interface.colors as colors
import assets


class Rect(object):
    """

    """

    def __init__(self, x, y, width, height, center=False):
        """

        Args:
            x (int):
            y (int):
            width (int):
            height (int):
            center (bool):
        """

        self.width = width
        self.height = height
        if not center:
            self.x = x
            self.y = y
        else:
            self.center = (x, y)

    def __str__(self):
        """

        Returns:
            str
        """
        return 'Rect{{x: {}, y: {}, width: {}, height: {}}}'.format(self.x, self.y, self.width, self.height)

    @property
    def center(self):
        """

        Returns:
            tuple
        """
        return self.x + self.width / 2, self.y + self.height / 2

    @center.setter
    def center(self, center):
        """

        Args:
            center (tuple):

        Returns:
            None
        """
        center_x, center_y = center
        self.x = center_x - self.width / 2
        self.y = center_y - self.height / 2

    @property
    def size(self):
        """

        Returns:
            tuple
        """
        return self.width, self.height

    @size.setter
    def size(self, size):
        """

        Args:
            size (tuple):

        Returns:
            None
        """
        self.width, self.height = size

    @property
    def bottom(self):
        """

        Returns:
            int
        """
        return self.y + self.height

    @bottom.setter
    def bottom(self, bottom):
        """

        Args:
            bottom (int):

        Returns:

        """
        self.y = bottom - self.height

    @property
    def right(self):
        """

        Returns:
            int
        """
        return self.x + self.width

    @right.setter
    def right(self, right):
        """

        Args:
            right (int):

        Returns:
            None
        """
        self.y = right - self.width

    @property
    def top(self):
        """

        Returns:
            int
        """
        return self.y

    @top.setter
    def top(self, top):
        """

        Args:
            top (int):

        Returns:
            None
        """
        self.y = top

    @property
    def left(self):
        """

        Returns:
            int
        """
        return self.x

    @left.setter
    def left(self, left):
        """

        Args:
            left (int):

        Returns:
            None
        """
        self.x = left

    def intersects(self, rect):
        """

        Args:
            rect (Rect):

        Returns:
            bool
        """
        return not (rect.left > self.right or
                    rect.right < self.left or
                    rect.top > self.bottom or
                    rect.bottom < self.top)


class Render(object):
    """
    [summary]  
    """

    def __init__(self, display_rect, board_rect, snakes, orbs):
        """

        Args:
            display_rect (pygame.Rect):
            board_rect (pygame.Rect):
            snakes (dictionary):
            orbs (dictionary):
        """
        self.display_rect = display_rect.copy()
        self.board_rect = board_rect.copy()
        self.camera_rect = Rect(display_rect.x, display_rect.y, display_rect.width, display_rect.height)
        self.snakes = snakes
        self.orbs = orbs
        self.player = None

    def get_offsets(self):
        """

        Returns:
            tuple
        """
        x, y = self.camera_rect.center
        xoff = -x + self.display_rect.width / 2.0
        yoff = -y + self.display_rect.height / 2.0
        return xoff, yoff

    def render(self, surface):
        """

        Args:
            surface (pygame.Surface):

        Returns:
            None
        """
        if self.player:
            self.camera_rect.center = self.player.location

        xoff, yoff = self.get_offsets()
        self.render_background(surface)
        self.render_orbs(surface, xoff, yoff)
        self.render_snakes(surface, xoff, yoff)

    def render_snakes(self, surface, xoff, yoff):
        """

        Args:
            surface (pygame.Surface):
            xoff (int):
            yoff (int):

        Returns:
            None
        """
        for snake in self.snakes.itervalues():
            for section in snake.tail + [snake.head]:
                rect = Rect(section.point.x, section.point.y, section.radius * 2, section.radius * 2, center=True)
                if rect.intersects(self.camera_rect):
                    snake.render(surface, xoff=xoff, yoff=yoff)
                    break

    def render_orbs(self, surface, xoff, yoff):
        """

        Args:
            surface (pygame.Surface):
            xoff (int):
            yoff (int):

        Returns:
            None
        """
        for orb in self.orbs.itervalues():
            rect = Rect(orb.point.x, orb.point.y, orb.radius * 2, orb.radius * 2, center=True)
            if rect.intersects(self.camera_rect):
                orb.render(surface, xoff=xoff, yoff=yoff)

    def render_background(self, surface):
        """

        Args:
            surface (pygame.Surface):

        Returns:
            None
        """
        surface.fill(colors.DEAD_RED)
        x = -self.camera_rect.x if self.camera_rect.x < 0 else 0
        y = -self.camera_rect.y if self.camera_rect.y < 0 else 0

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
    """

    Args:
        surface (pygame.Surface):
        text (str):
        x (int):
        y (int):
        size (int):
        color (tuple):
        center (bool):

    Returns:
        None
    """
    font = pygame.font.Font(assets.Font_Segoe_UI, size)
    textSurface = font.render(text, True, color)
    TextRect = textSurface.get_rect()
    if center:
        TextRect.center = (x, y)
    else:
        TextRect.topleft = (x, y)
    surface.blit(textSurface, TextRect)
