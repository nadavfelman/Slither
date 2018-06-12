from __builtin__ import super

import pygame
from string import printable

BLACK = (0, 0, 0)
GRAY2 = (85, 85, 85)
GRAY1 = (170, 170, 170)
WHITE = (255, 255, 255)


class BaseElement(object):
    """

    """

    def __init__(self):
        self.need_rerender = False
        self.need_update = False
        self.need_events = False
        self.need_closing = False

    def render(self, surface):
        pass

    def update(self):
        pass

    def handle_event(self, event):
        pass

    def close(self):
        pass


class Button(BaseElement):
    """
    [summary]
    """

    FONT_SIZE = 48
    FONT_NAME = None

    COLOR_REGULAR = WHITE
    COLOR_HOVER = GRAY1
    COLOR_CLICK = GRAY2
    COLOR_SECONDARY = BLACK

    def __init__(self, x, y, w, h, text='', text_color=None, regular=None,
                 hover=None, click=None, border_color=None,
                 border_size=None, fnc=None, font_name=None,
                 font_size=None):

        super(Button, self).__init__()

        self.rect = pygame.Rect(int(round(x)), int(round(y)),
                                int(round(w)), int(round(h)))
        self.text = text
        self.text_color = text_color or Button.COLOR_SECONDARY

        self.font = pygame.font.Font(font_name or Button.FONT_NAME,
                                     int(round(font_size or Button.FONT_SIZE)))
        self.txt_surface = self.font.render(self.text, True, self.text_color)

        self.regular = regular or Button.COLOR_REGULAR
        self.hover = hover or Button.COLOR_HOVER
        self.click = click or Button.COLOR_CLICK

        self.border_color = border_color or Button.COLOR_SECONDARY
        self.border_size = int(round(border_size or 0))

        self.fnc = fnc

    def on_button(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def has_clicked(self):
        return self.on_button() and pygame.mouse.get_pressed()[0]

    def update(self):
        if self.has_clicked() and callable(self.fnc):
            self.fnc()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.rect.collidepoint(event.pos) and callable(self.fnc):
                    self.fnc()

    def render(self, surface):
        if self.on_button():
            if pygame.mouse.get_pressed()[0]:
                self.render_clicked(surface)
            else:
                self.render_hover(surface)
        else:
            self.render_regular(surface)

        if self.border_size:
            pygame.draw.rect(surface, self.border_color,
                             self.rect, self.border_size)

        if self.text:
            self.render_text(surface)

    def render_regular(self, surface):
        pygame.draw.rect(surface, self.regular, self.rect, 0)

    def render_hover(self, surface):
        pygame.draw.rect(surface, self.hover, self.rect, 0)

    def render_clicked(self, surface):
        pygame.draw.rect(surface, self.click, self.rect, 0)

    def render_text(self, surface):
        txt_rect = self.txt_surface.get_rect()
        txt_rect.center = self.rect.center
        surface.blit(self.txt_surface, txt_rect.topleft)


class InputBox(BaseElement):
    """
    [summary]
    """

    COLOR_BASE = WHITE
    COLOR_ACTIVE = GRAY1
    COLOR_INACTIVE = GRAY2
    COLOR_TEXT_ACTIVE = GRAY1
    COLOR_TEXT_INACTIVE = GRAY2
    FONT_SIZE = 48
    FONT_NAME = None
    BORDER_SIZE = 0

    def __init__(self, x, y, w, h, text='', base_color=None,
                 active_color=None, inactive_color=None,
                 active_tcolor=None, inactive_tcolor=None,
                 font_name=None, font_size=None, border_size=None):

        super(InputBox, self).__init__()

        self.base_color = base_color or InputBox.COLOR_BASE
        self.active_color = active_color or InputBox.COLOR_ACTIVE
        self.inactive_color = inactive_color or InputBox.COLOR_INACTIVE
        self.active_tcolor = active_tcolor or InputBox.COLOR_TEXT_ACTIVE
        self.inactive_tcolor = inactive_tcolor or InputBox.COLOR_TEXT_INACTIVE
        self.color = self.inactive_color
        self.tcolor = self.inactive_tcolor

        self.font_size = int(round(font_size or InputBox.FONT_SIZE))
        self.font = pygame.font.Font(font_name or InputBox.FONT_NAME, self.font_size)
        self.default_text = text
        self.text = text
        self.txt_surface = self.font.render(text, True, self.tcolor)
        self.border_size = int(round(border_size or InputBox.BORDER_SIZE))

        self.rect = pygame.Rect(int(round(x)), int(round(y)), int(round(w)), int(round(h)))
        self.active = False
        self.done_action = False
        self.mirgins = [int(round(h)) / 2 - self.font.get_height() / 2, 0.4 * self.font_size]
        self.limit = 16

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
                if not self.active:
                    self.done_action = False
                    if self.text == '':
                        self.text = self.default_text
            else:
                self.active = False
                self.done_action = False
                if self.text == '':
                    self.text = self.default_text

            # Change the current color of the input box.
            self.color = self.active_color if self.active else self.inactive_color
            self.tcolor = self.active_tcolor if self.active else self.inactive_tcolor
            self.txt_surface = self.font.render(
                self.text, True, self.tcolor)

        if event.type == pygame.KEYDOWN:
            if self.active:
                if not self.done_action:
                    if self.text == self.default_text:
                        self.done_action = True
                        self.text = ''
                if event.key == pygame.K_ESCAPE:
                    self.active = False
                    self.done_action = False
                    self.color = self.inactive_color
                    self.tcolor = self.inactive_tcolor
                    if self.text == '':
                        self.text = self.default_text
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < self.limit:
                        if event.unicode in printable:
                            blocked = '\t\n\r'
                            if event.unicode not in blocked:
                                self.text += event.unicode
                # Re-render the text.
                self.txt_surface = self.font.render(
                    self.text, True, self.tcolor)

    def render(self, screen):
        pygame.draw.rect(screen, self.base_color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + self.mirgins[1],
                                       self.rect.y + self.mirgins[0]))
        if self.border_size:
            pygame.draw.rect(screen, self.color, self.rect, self.border_size)


class Container(BaseElement):
    """
    [summary]
    """

    COLOR_BASE = WHITE
    COLOR_SECONDARY = BLACK
    BORDER_SIZE = 0

    def __init__(self, x, y, w, h, color=None, border_color=None, border_size=None):
        super(Container, self).__init__()

        self.rect = pygame.Rect(int(round(x)), int(
            round(y)), int(round(w)), int(round(h)))
        self.color = color or Container.COLOR_BASE
        self.border_color = border_color or Container.COLOR_SECONDARY
        self.border_size = int(round(border_size or Container.BORDER_SIZE))

    def render(self, display):
        pygame.draw.rect(display, self.color, self.rect)
        if self.border_size:
            pygame.draw.rect(display, self.border_color,
                             self.rect, self.border_size)


class Text(BaseElement):
    """
    [summary]
    """

    COLOR = BLACK
    FONT_NAME = None
    SIZE = 48

    def __init__(self, x, y, text, font_name=None, size=None, color=None, center=False):
        super(Text, self).__init__()

        self.font = pygame.font.Font(
            font_name or Text.FONT_NAME, int(round(size or Text.SIZE)))
        self._text = ''
        self.text_surfaces = []

        self.center = center
        self.color = color or Text.COLOR
        self.x = int(round(x))
        self.y = int(round(y))

        self.text = text

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        self._text = text
        self.text_surfaces = []

        lines = text.split('\n')
        for line in lines:
            text_surface = self.font.render(line, True, self.color)
            self.text_surfaces.append(text_surface)

    def render(self, surface):
        for line_num, text_surface in enumerate(self.text_surfaces):
            text_rect = text_surface.get_rect()
            pos = (self.x, self.y + (line_num * self.font.get_height()))
            if self.center:
                text_rect.center = pos
            else:
                text_rect.topleft = pos
            surface.blit(text_surface, text_rect)


class Image(BaseElement):
    """
    [summary]
    """

    def __init__(self, x, y, image_path, scale=1):
        super(Image, self).__init__()

        self.x = int(round(x))
        self.y = int(round(y))
        self.image = pygame.image.load(image_path).convert()
        new_size = (int(round(self.image.get_width() * scale)),
                    int(round(self.image.get_height() * scale)))
        self.image = pygame.transform.smoothscale(
            self.image, new_size).convert()

    def render(self, surface):
        surface.blit(self.image, (self.x, self.y))


class Line(BaseElement):
    """
    [summary]
    """

    COLOR = BLACK
    WIDTH = 1

    def __init__(self, x1, y1, x2, y2, width=None, color=None):
        super(Line, self).__init__()

        self.start_pos = (int(round(x1)), int(round(y1)))
        self.end_pos = (int(round(x2)), int(round(y2)))
        self.width = int(round(width or Line.WIDTH))
        self.color = color or Line.COLOR

    def render(self, surface):
        pygame.draw.line(surface, self.color, self.start_pos,
                         self.end_pos, self.width)


class Screen(object):
    """
    this serves as the base to screens objects.
    this adds the functionality to the screens.

    when inheriting needed actions to make:
        # create buttons` functions
        # create screen elements
        # set rerendering
        # set update
        # set event handling
        # set closing
        # create subwindows
        # assign buttons their function
        # initialize variables
        # add screen elements to the elements array
        # add sub windows to windows array
        # set active sub windows
    """

    def __init__(self):
        self.elements_objs = []
        self.windows_objs = []

        self.next_render_full = True
        self.active = True

    def render(self, surface):
        if self.next_render_full:
            self.full_render(surface)
            self.next_render_full = False
        else:
            self.partial_render(surface)

    def full_render(self, surface):
        # stack = inspect.stack()
        # the_class = stack[1][0].f_locals["self"].__class__
        # the_method = stack[1][0].f_code.co_name
        # print 'full render {}.{} on {}'.format(str(the_class), the_method, self.__class__)

        for element in self.elements_objs:
            element.render(surface)

        for window in self.windows_objs:
            if window.active:
                window.next_render_full = True
                window.render(surface)

    def partial_render(self, surface):
        # stack = inspect.stack()
        # the_class = stack[1][0].f_locals["self"].__class__
        # the_method = stack[1][0].f_code.co_name
        # print '\tpartial render {}.{} on {}'.format(str(the_class), the_method, self.__class__)

        for element in self.elements_objs:
            if getattr(element, 'need_rerender', None):
                element.render(surface)

        for window in self.windows_objs:
            if window.active:
                window.render(surface)

    def update(self):
        for element in self.elements_objs:
            if getattr(element, 'need_update', None):
                element.update()

        for window in self.windows_objs:
            if window.active:
                window.update()

    def handle_event(self, event):
        for element in self.elements_objs:
            if getattr(element, 'need_events', None):
                element.handle_event(event)

        for window in self.windows_objs:
            if window.active:
                window.handle_event(event)

    def close(self):
        for element in self.elements_objs:
            if getattr(element, 'need_closing', None):
                element.close()

        for window in self.windows_objs:
            if window.active:
                window.close()

    def set_actives(self, *args):
        for window in self.windows_objs:
            if window in args:
                window.active = True
                window.next_render_full = True
            else:
                window.active = False
