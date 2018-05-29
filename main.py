import ctrlVars
import pygame
import interface


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
    ps = interface.screens.control_screen(WINDOW_WIDTH, WINDOW_HEIGHT)
    ps.render(display)

    while ctrlVars.running:
        key_mods = pygame.key.get_mods()
        alt_held = key_mods & pygame.KMOD_ALT
        ctrl_held = key_mods & pygame.KMOD_CTRL

        for event in pygame.event.get():
            # exit if pressed on the X (top right)
            if event.type == pygame.QUIT:
                ctrlVars.running = False
            # handel key presses
            elif event.type == pygame.KEYDOWN:
                # exit if press alt-f4 or ctrl-w
                if event.key == pygame.K_w and ctrl_held:
                    ctrlVars.running = False
                elif event.key == pygame.K_F4 and alt_held:
                    ctrlVars.running = False
            ps.handle_event(event)

        ps.update()
        ps.render(display)
        pygame.display.flip()
        CLOCK.tick(60)


if __name__ == '__main__':
    main()
