import ctrlVars
import pygame
import interface


def close(screen_control):
    ctrlVars.running = False
    screen_control.close()


def main():
    # pygame inizializition
    # display set up
    pygame.init()
    infoObject = pygame.display.Info()
    WINDOW_WIDTH = infoObject.current_w
    WINDOW_HEIGHT = infoObject.current_h
    flags = pygame.FULLSCREEN | pygame.HWSURFACE
    display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    display.set_alpha(None)
    CLOCK = pygame.time.Clock()
    screen_control = interface.screens.control_screen(WINDOW_WIDTH, WINDOW_HEIGHT)
    screen_control.render(display)

    while ctrlVars.running:
        # key press
        key_mods = pygame.key.get_mods()
        alt_held = key_mods & pygame.KMOD_ALT
        ctrl_held = key_mods & pygame.KMOD_CTRL

        for event in pygame.event.get():
            # exit if pressed on the X (top right)
            if event.type == pygame.QUIT:
                close(screen_control)
            # handel key presses
            elif event.type == pygame.KEYDOWN:
                # exit if press alt-f4 or ctrl-w
                if event.key == pygame.K_w and ctrl_held:
                    close(screen_control)
                elif event.key == pygame.K_F4 and alt_held:
                    close(screen_control)
            screen_control.handle_event(event)

        if ctrlVars.running:
            screen_control.update()
            screen_control.render(display)
            pygame.display.flip()
            CLOCK.tick(60)


if __name__ == '__main__':
    main()
