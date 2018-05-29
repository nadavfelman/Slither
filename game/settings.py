import pygame
pygame.display.init()

infoObject = pygame.display.Info()

WINDOW_WIDTH = infoObject.current_w
WINDOW_HEIGHT = infoObject.current_h

WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_CENTER = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

REFRESH_RATE = 60
