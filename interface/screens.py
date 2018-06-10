import elements
import assets
import colors
import ctrlVars
import connection
import re
import subprocess
import time
import pygame


class ControlScreen(elements.Screen):
    """
    [summary]
    """

    def __init__(self, w, h):
        # create the functions
        def multiplayer_win_join_button():
            self.set_actives(self.multiplayer_join)

        def multiplayer_join_cancel_button():
            self.set_actives(self.main_win)

        def multiplayer_join_join_button():
            name = self.main_win.inputbox.text
            ip = self.multiplayer_join.inputbox.text

            if ip != 'localhost':
                match = re.match(r'(\d{1,3}\.){3}\d{1,3}', ip)
                if not match:
                    return

                sections = ip.split('.')
                valid = all([0 <= int(num) <= 255 for num in sections])
                if not valid:
                    return

            self.game = GameWindow(w, h, ip, name)
            self.game.game_start_sub.cancel_button.fnc = game_exit
            self.windows_objs.append(self.game)
            self.set_actives(self.game)

        def singleplayer_join():
            subprocess.Popen(['start', 'cmd', '/c', 'python', '.\server.py'],
                             shell=True, stdin=None, stdout=None,
                             stderr=None, close_fds=True)
            time.sleep(1.6)
            # os.system(r"start /wait cmd /c python .\connection\server.py")
            name = self.main_win.inputbox.text
            self.game = GameWindow(w, h, '127.0.0.1', name)
            self.game.game_start_sub.cancel_button.fnc = game_exit
            self.windows_objs.append(self.game)
            self.set_actives(self.game)

        def game_exit():
            self.game.close()
            self.game = None
            self.set_actives(self.main_win)

        # create subwindows
        self.game = None
        self.main_win = PrimaryScreen(w, h)
        self.multiplayer_join = MultiplayerConnection(w, h)

        self.main_win.multiplayer_win.start_button.fnc = multiplayer_win_join_button
        self.multiplayer_join.cancel_button.fnc = multiplayer_join_cancel_button
        self.multiplayer_join.join_button.fnc = multiplayer_join_join_button
        self.main_win.singleplayer_win.start_button.fnc = singleplayer_join

        # initialize variables
        super(ControlScreen, self).__init__()

        self.windows_objs.append(self.main_win)
        self.windows_objs.append(self.multiplayer_join)

        self.set_actives(self.main_win)

    def multiplayer_win_join_button(self):
        self.set_actives(self.multiplayer_join)


class PrimaryScreen(elements.Screen):
    """
    [summary]
    """

    def __init__(self, w, h):
        # create the functions
        def stop_running():
            ctrlVars.running = False

        def show_singleplayer_win():
            self.set_actives(self.singleplayer_win)

        def show_multiplayer_win():
            self.set_actives(self.multiplayer_win)

        # create the elements
        self.background = elements.Image(0, 0, assets.primary_bg,
                                         scale=w / 1920.0)

        self.button_singleplayer = elements.Button(0.044270 * w,
                                                   0.553703 * h, 0.271354 * w, 0.070370 * h,
                                                   'singleplayer',
                                                   text_color=colors.GRAY235,
                                                   regular=colors.GRAY92,
                                                   hover=colors.BLUE,
                                                   click=colors.BLUE_BASIC,
                                                   font_name=assets.primary_font,
                                                   font_size=0.044444 * h,
                                                   fnc=show_singleplayer_win)

        self.button_multiplayer = elements.Button(0.044270 * w, 0.642592 * h,
                                                  0.271354 * w, 0.070370 * h, 'multiplayer',
                                                  text_color=colors.GRAY235,
                                                  regular=colors.GRAY92,
                                                  hover=colors.BLUE,
                                                  click=colors.BLUE_BASIC,
                                                  font_name=assets.primary_font,
                                                  font_size=0.044444 * h,
                                                  fnc=show_multiplayer_win)

        self.button_exit = elements.Button(0.044270 * w, 0.731481 * h,
                                           0.271354 * w, 0.070370 * h, 'exit',
                                           text_color=colors.GRAY235,
                                           regular=colors.RED68,
                                           hover=colors.RED54,
                                           click=colors.RED38,
                                           fnc=stop_running,
                                           font_name=assets.primary_font,
                                           font_size=0.044444 * h)

        self.inputbox = elements.InputBox(0.034375 * w, 0.372222 * h,
                                          0.291145 * w, 0.075 * h, 'nickname',
                                          base_color=colors.GRAY235,
                                          active_color=colors.BLUE,
                                          inactive_color=colors.GRAY92,
                                          active_tcolor=colors.FLAT_BLUE,
                                          inactive_tcolor=colors.GRAY215,
                                          font_name=assets.primary_font,
                                          font_size=0.044444 * h,
                                          border_size=0.001852 * h)

        self.buttons_container = elements.Container(0.034375 * w, 0.469444 * h,
                                                    0.291145 * w, 0.350925 * h,
                                                    color=colors.GRAY235,
                                                    border_color=colors.GRAY92,
                                                    border_size=0.001852 * h)

        self.game_text = elements.Text(0.103125 * w, 0.473148 * h,
                                       'Join a Game', assets.primary_font_bold,
                                       0.050925 * h, colors.GRAY92)

        self.name_text = elements.Text(0.034375 * w, 0.078703 * h,
                                       'Slither.all', assets.Font_Segoe_Script,
                                       0.185185 * h, colors.GRAY235)

        # set rerendering
        self.button_singleplayer.need_rerender = True
        self.button_multiplayer.need_rerender = True
        self.button_exit.need_rerender = True
        self.inputbox.need_rerender = True

        # set update

        # set event handling
        self.button_singleplayer.need_events = True
        self.button_multiplayer.need_events = True
        self.button_exit.need_events = True
        self.inputbox.need_events = True

        # create subwindows
        self.singleplayer_win = SingleplayerInfo(w, h)
        self.multiplayer_win = MultiplayerInfo(w, h)

        # initialize variables
        super(PrimaryScreen, self).__init__()

        self.elements_objs.append(self.background)
        self.elements_objs.append(self.buttons_container)
        self.elements_objs.append(self.button_singleplayer)
        self.elements_objs.append(self.button_multiplayer)
        self.elements_objs.append(self.button_exit)
        self.elements_objs.append(self.inputbox)
        self.elements_objs.append(self.game_text)
        self.elements_objs.append(self.name_text)

        self.windows_objs.append(self.singleplayer_win)
        self.windows_objs.append(self.multiplayer_win)

        self.set_actives()


class SingleplayerInfo(elements.Screen):
    """[summary]

    Arguments:
        screen {[type]} -- [description]
    """

    def __init__(self, w, h):
        # create the elements
        self.container = elements.Container(0.338541 * w, 0.372222 * h,
                                            0.625 * w, 0.447222 * h,
                                            color=colors.GRAY235,
                                            border_color=colors.GRAY92,
                                            border_size=0.001852 * h)

        self.title = elements.Text(0.348958 * w, 0.384259 * h, 'Singleplayer',
                                   assets.Font_Segoe_UI_Semilight,
                                   0.050925 * h, colors.GRAY66)

        text = 'This will start a singleplayer type game.\nIn this mode ' \
               'the player does not face another human\nplayers. In this ' \
               'mode NO INTERNET CONNECTION IS\nNEEDED. '
        self.text = elements.Text(0.348958 * w, 0.472222 * h, text,
                                  assets.Font_Segoe_UI_Light, 0.046296 * h,
                                  colors.GRAY92)

        self.start_button = elements.Button(0.348958 * w, 0.731481 * h,
                                            0.270833 * w, 0.070370 * h,
                                            text='start',
                                            text_color=colors.GRAY92,
                                            regular=colors.GREEN_FL,
                                            hover=colors.GREEN_FLST,
                                            click=colors.GREEN_FLSTDE,
                                            font_name=assets.Font_Segoe_UI_Light,
                                            font_size=0.050926 * h)

        self.line = elements.Line(0.348958 * w, 0.46 * h,
                                  0.947917 * w, 0.46 * h,
                                  width=0.001852 * h,
                                  color=colors.GRAY173)

        # set rerendering
        self.start_button.need_rerender = True

        # set update

        # set event handling
        self.start_button.need_events = True

        # initialize variables
        super(SingleplayerInfo, self).__init__()

        self.elements_objs.append(self.container)
        self.elements_objs.append(self.line)
        self.elements_objs.append(self.title)
        self.elements_objs.append(self.text)
        self.elements_objs.append(self.start_button)


class MultiplayerInfo(elements.Screen):
    """
    [summary]
    """

    def __init__(self, w, h):
        # create the elements
        self.container = elements.Container(0.338541 * w, 0.372222 * h,
                                            0.625 * w, 0.447222 * h,
                                            color=colors.GRAY235,
                                            border_color=colors.GRAY92,
                                            border_size=0.001852 * h)

        self.title = elements.Text(0.348958 * w, 0.384259 * h, 'Multiplayer',
                                   assets.Font_Segoe_UI_Semilight, 0.050925 * h,
                                   colors.GRAY66)

        text = 'This will start a multiplaer type game.\nIn this mode the ' \
               'player faces another human\nplayers. In this mode ' \
               'INTERNET CONNECTION IS\nNEEDED to play in this mode. '
        self.text = elements.Text(0.348958 * w, 0.472222 * h, text,
                                  assets.Font_Segoe_UI_Light, 0.046296 * h,
                                  colors.GRAY92)

        self.start_button = elements.Button(0.348958 * w, 0.731481 * h,
                                            0.270833 * w, 0.070370 * h,
                                            text='connect',
                                            text_color=colors.GRAY92,
                                            regular=colors.GREEN_FL,
                                            hover=colors.GREEN_FLST,
                                            click=colors.GREEN_FLSTDE,
                                            font_name=assets.Font_Segoe_UI_Light,
                                            font_size=0.050926 * h)

        self.line = elements.Line(0.348958 * w, 0.46 * h, 0.947917 * w,
                                  0.46 * h,
                                  width=0.001852 * h,
                                  color=colors.GRAY173)

        # set rerendering
        self.start_button.need_rerender = True

        # set update

        # set event handling
        self.start_button.need_events = True

        # initialize variables
        super(MultiplayerInfo, self).__init__()

        self.elements_objs.append(self.container)
        self.elements_objs.append(self.line)
        self.elements_objs.append(self.title)
        self.elements_objs.append(self.text)
        self.elements_objs.append(self.start_button)


class MultiplayerConnection(elements.Screen):
    """
    [summary]
    """

    def __init__(self, w, h):
        # create the elements
        self.background = elements.Image(0, 0, assets.primary_bg,
                                         scale=w / 1920.0)

        self.container = elements.Container(0.187500 * w, 0.296296 * h,
                                            0.625000 * w, 0.462963 * h,
                                            color=colors.GRAY235,
                                            border_color=colors.GRAY92,
                                            border_size=0.001852 * h)

        self.title = elements.Text(0.200000 * w, 0.305556 * h,
                                   'Multiplayer Connection',
                                   assets.Font_Segoe_UI_Semilight,
                                   0.050925 * h, colors.GRAY66)

        text = 'Please enter the server`s IP in the input box below.\n' \
               'Make sure the server is in your LAN or can be accessed\n' \
               'from the internet.'
        self.text = elements.Text(0.200000 * w, 0.376852 * h, text,
                                  assets.Font_Segoe_UI_Light, 0.046296 * h,
                                  colors.GRAY92)

        self.join_button = elements.Button(0.200000 * w, 0.663889 * h,
                                           0.476042 * w, 0.070370 * h,
                                           text='join',
                                           text_color=colors.GRAY92,
                                           regular=colors.GREEN_FL,
                                           hover=colors.GREEN_FLST,
                                           click=colors.GREEN_FLSTDE,
                                           font_name=assets.Font_Segoe_UI_Light,
                                           font_size=0.050926 * h)

        self.cancel_button = elements.Button(0.684375 * w, 0.663889 * h,
                                             0.107292 * w, 0.070370 * h, 'cancel',
                                             text_color=colors.GRAY235,
                                             regular=colors.RED68,
                                             hover=colors.RED54,
                                             click=colors.RED38,
                                             font_name=assets.primary_font,
                                             font_size=0.044444 * h)

        self.line = elements.Line(0.200000 * w, 0.379630 * h, 0.770833 * w,
                                  0.379630 * h,
                                  width=0.001852 * h,
                                  color=colors.GRAY173)

        self.inputbox = elements.InputBox(0.200000 * w, 0.571296 * h,
                                          0.592708 * w, 0.070370 * h, 'server`s ip',
                                          base_color=colors.GRAY235,
                                          active_color=colors.BLUE,
                                          inactive_color=colors.GRAY92,
                                          active_tcolor=colors.FLAT_BLUE,
                                          inactive_tcolor=colors.GRAY215,
                                          font_name=assets.primary_font,
                                          font_size=0.044444 * h,
                                          border_size=0.001852 * h)

        # set rerendering
        self.join_button.need_rerender = True
        self.cancel_button.need_rerender = True
        self.inputbox.need_rerender = True

        # set update

        # set event handling
        self.join_button.need_events = True
        self.cancel_button.need_events = True
        self.inputbox.need_events = True

        # initialize variables
        super(MultiplayerConnection, self).__init__()

        self.elements_objs.append(self.background)
        self.elements_objs.append(self.container)
        self.elements_objs.append(self.title)
        self.elements_objs.append(self.line)
        self.elements_objs.append(self.text)
        self.elements_objs.append(self.inputbox)
        self.elements_objs.append(self.join_button)
        self.elements_objs.append(self.cancel_button)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.join_button.fnc()
            elif event.key == pygame.K_ESCAPE:
                self.cancel_button.fnc()
        super(MultiplayerConnection, self).handle_event(event)


class GameWindow(elements.Screen):
    """[summary]
    
    Arguments:
        elements {[type]} -- [description]
    """

    def __init__(self, w, h, ip, name):
        def info_update():
            player = self.client.get_player()
            if player:
                self.game_gui.player_info.text = 'Current mass: ' + str(player.mass)

        def leaderboard_update():
            string = ''
            string += 'Players Leaderboard:\n'
            count = 0

            for snake in sorted(self.client.snakes.itervalues(), key=lambda s: s.mass, reverse=True):
                if not count < 10:
                    continue
                string += '{}. {}\n'.format(count + 1, snake.name)
                count += 1

            for i in xrange(count, 10):
                string += '{}.\n'.format(count + 1)
                count += 1

            self.game_gui.leaderboard.text = string

        self.client = connection.client.Client(ip, name)
        self.game_gui = GameGUI(w, h)
        self.game_start_sub = GameStartSubwindow(w, h)

        self.game_gui.player_info.update = info_update
        self.game_gui.leaderboard.update = leaderboard_update
        self.game_start_sub.join_button.fnc = self.client.start_game

        # set rerendering
        self.client.need_rerender = True

        # set update
        self.client.need_update = True

        # set event handling

        # set closing
        self.client.need_closing = True

        # initialize variables
        super(GameWindow, self).__init__()

        self.elements_objs.append(self.client)

        self.windows_objs.append(self.game_gui)
        self.windows_objs.append(self.game_start_sub)

        self.set_actives(self.game_start_sub)

    def update(self):
        if self.client.key not in self.client.snakes:
            self.set_actives(self.game_start_sub)
        else:
            self.set_actives(self.game_gui)
        super(GameWindow, self).update()


class GameGUI(elements.Screen):
    """

    """

    def __init__(self, w, h):
        self.info_container = elements.Container(0.006 * w, 0.0085 * h,
                                                 0.12 * w, 0.03 * h,
                                                 color=colors.GRAY235,
                                                 border_color=colors.GRAY173,
                                                 border_size=0.001852 * h)

        self.player_info = elements.Text(0.01 * w, 0.0085 * h, '',
                                         assets.Font_Segoe_UI_Semilight, 0.02 * h,
                                         colors.GRAY40)

        self.leaderboard_container = elements.Container(0.006 * w, 0.05 * h,
                                                        0.12 * w, 0.31 * h,
                                                        color=colors.GRAY235,
                                                        border_color=colors.GRAY173,
                                                        border_size=0.001852 * h)

        self.leaderboard = elements.Text(0.01 * w, 0.05 * h, '',
                                         assets.Font_Segoe_UI_Semilight, 0.02 * h,
                                         colors.GRAY40)

        # set rerendering
        self.player_info.need_rerender = True
        self.leaderboard.need_rerender = True
        self.info_container.need_rerender = True
        self.leaderboard_container.need_rerender = True

        # set update
        self.player_info.need_update = True
        self.leaderboard.need_update = True

        # set event handling

        # set closing

        # initialize variables
        super(GameGUI, self).__init__()

        self.elements_objs.append(self.leaderboard_container)
        self.elements_objs.append(self.info_container)
        self.elements_objs.append(self.player_info)
        self.elements_objs.append(self.leaderboard)


class GameStartSubwindow(elements.Screen):
    """
    [summary]
    """

    def __init__(self, w, h):
        # create the elements
        self.container = elements.Container(0.180729 * w, 0.312963 * h,
                                            0.625000 * w, 0.375000 * h,
                                            color=colors.GRAY235,
                                            border_color=colors.GRAY92,
                                            border_size=0.001852 * h)

        self.title = elements.Text(0.192708 * w, 0.324074 * h,
                                   'Game',
                                   assets.Font_Segoe_UI_Semilight,
                                   0.050925 * h, colors.GRAY66)

        text = "You successfully connected to the server.\n" \
               "Press start to spawn into the game and start playing.\n" \
               "Press exit to close the game."
        self.text = elements.Text(0.192708 * w, 0.393519 * h, text,
                                  assets.Font_Segoe_UI_Light, 0.046296 * h,
                                  colors.GRAY92)

        self.join_button = elements.Button(0.192708 * w, 0.597222 * h,
                                           0.476042 * w, 0.070370 * h,
                                           text='start',
                                           text_color=colors.GRAY92,
                                           regular=colors.GREEN_FL,
                                           hover=colors.GREEN_FLST,
                                           click=colors.GREEN_FLSTDE,
                                           font_name=assets.Font_Segoe_UI_Light,
                                           font_size=0.050926 * h)

        self.cancel_button = elements.Button(0.677083 * w, 0.597222 * h,
                                             0.107292 * w, 0.070370 * h, 'exit',
                                             text_color=colors.GRAY235,
                                             regular=colors.RED68,
                                             hover=colors.RED54,
                                             click=colors.RED38,
                                             font_name=assets.primary_font,
                                             font_size=0.044444 * h)

        self.line = elements.Line(0.192708 * w, 0.396296 * h, 0.789583 * w,
                                  0.396296 * h,
                                  width=0.001852 * h,
                                  color=colors.GRAY173)

        # set rerendering
        self.join_button.need_rerender = True
        self.cancel_button.need_rerender = True

        # set update

        # set event handling
        self.join_button.need_events = True
        self.cancel_button.need_events = True

        # initialize variables
        super(GameStartSubwindow, self).__init__()

        self.elements_objs.append(self.container)
        self.elements_objs.append(self.title)
        self.elements_objs.append(self.line)
        self.elements_objs.append(self.text)
        self.elements_objs.append(self.join_button)
        self.elements_objs.append(self.cancel_button)
