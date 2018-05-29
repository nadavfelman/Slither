import math
import random

import pygame

import dataSets
import functions
import objects
import render
import settings
import threading
import protocol
import socket
import time


# class main_thread(threading.Thread):
#     """
#     [summary]
#     """
# 
#     def __init__(self, socket_):
#         """[summary]
# 
#         Arguments:
#             socket_ {socket.socket} -- [description]
#             address {[type]} -- [description]
#             id_ {[type]} -- [description]
#         """
# 
#         super(main_thread, self).__init__()
#         self.socket_ = socket_
# 
#     def run(self):
#         message = protocol.parse(protocol.recv_data(self.socket_))
#         if message.get('type', None) == protocol.Type.ID and message.get('subtype', None) == protocol.Subtype.ID.send:
#             self.id_ = message['id']
#             protocol.send_data(self.socket_, protocol.id_confirm())
# 
#         while True:
#             message = protocol.parse(protocol.recv_data(self.socket_))
#             if message.get('type', None) == protocol.Type.BOARD and message.get('subtype', None) == protocol.Subtype.BOARD.send_dimensions:
#                 self.board_width = message['width']
#                 self.board_height = message['height']
#                 protocol.send_data(self.socket_, protocol.board_confirm_dimensions())
# 
#         com = socket.socket()
#         com.bind(('0.0.0.0', 44326))
#         com.listen(0)
#         receiver, _ = com.accept()
#         sender, _ = com.accept()
#         com.close()
# 
# 
#         self.receiver = receiving_thread(receiver, self.address, self.id_)
#         self.receiver.start()
#         self.sender = sending_thread(sender, self.address, self.id_)
#         self.sender.start()
# 
#         self.receiver.join()
#         self.sender.join()


def main():
    # pygame inizializition
    pygame.init()

    # display set up
    flags = pygame.FULLSCREEN | pygame.HWSURFACE
    display = pygame.display.set_mode(settings.WINDOW_SIZE, flags)
    display.set_alpha(None)

    # data setup
    CLOCK = pygame.time.Clock()
    board = pygame.Rect(0, 0, 200, 200)
    dataBase = dataSets.dataBase()
    rendering = render.render(display.get_rect(), board, dataBase)

    # test s
    player = objects.playerSnake((100, 100), 'nadav')
    dataBase.add_snake('1', player)
    rendering.set_player(player)

    for i in xrange(100):
        dataBase.add_orb(i, objects.orb(random.randint(0, 200), random.randint(
            0, 200), random.randint(2, 20), random.choice(objects.orb.ORB_COLORS)))

    while True:
        # console prints
        if True or CLOCK.get_fps() < settings.REFRESH_RATE * 0.8:
            print 'fps: {}'.format(CLOCK.get_fps())

        # event handling
        # get integer with all the key mods, then use and operations to compare.
        key_mods = pygame.key.get_mods()
        # save states of alt, ctrl and shift key
        alt_held = key_mods & pygame.KMOD_ALT
        ctrl_held = key_mods & pygame.KMOD_CTRL
        shift_held = key_mods & pygame.KMOD_SHIFT

        for event in pygame.event.get():
            # exit if pressed on the X (top right)
            if event.type == pygame.QUIT:
                return
            # handel key presses
            elif event.type == pygame.KEYDOWN:
                # exit if press alt-f4 or ctrl-w
                if event.key == pygame.K_w and ctrl_held:
                    return
                elif event.key == pygame.K_F4 and alt_held:
                    return
                # other

        # game handling
        mouse_loc = pygame.mouse.get_pos()
        middle_loc = settings.WINDOW_CENTER
        new_angle = functions.incline_angle(mouse_loc, middle_loc)
        player.set_angle(new_angle, limit=objects.playerSnake.MAX_ANGLE_CHANGE)
        player.move()

        for id_, obj in list(dataBase.iter_orbs()):
            collide = player.any_collide(obj)
            if collide:
                dataBase.remove_orb(id_)
                player.add_mass(obj.mass)

        if player.boarders_collide(board):
            del(player)

        # screen update
        rendering.set_camera_pos(player.get_location())
        rendering.set_zoom(settings.WINDOW_HEIGHT * .03 /
                           player.get_radius() + 1)
        rendering.render(display)
        pygame.display.flip()

        # tick timer
        CLOCK.tick(settings.REFRESH_RATE)


if __name__ == '__main__':
    main()
