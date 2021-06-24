import socket
import sys
from threading import Thread

import pygame as pyg

import game_objects
import obstacles
import player
import power_ups

from consts import *


class Game:
    """
    Main game class
    Handles all game-related constants and game logistics
    Interacts with the server
    """
    WIDTH: int = 600
    HEIGHT: int = 600
    GRAVITY: float = 0.3
    FPS: int = 60
    TITLE: str = 'Dyber'

    COLOR_BLACK: tuple = (0, 0, 0)
    COLOR_WHITE: tuple = (255, 255, 255)
    COLOR_BACKGROUND: tuple = (200, 200, 200)
    COLOR_PLAYER_RED: tuple = (200, 0, 0)
    COLOR_PLAYER_PURPLE: tuple = (118, 6, 204)
    COLOR_PLAYER_GREEN: tuple = (23, 110, 8)
    COLOR_PLAYER_BROWN: tuple = (79, 46, 5)
    COLOR_BLOCK: tuple = (100, 100, 100)
    COLOR_DOOR: tuple = (100, 50, 50)
    COLOR_KEY: tuple = (190, 190, 50)
    COLOR_GRAVITY_ROTATOR: tuple = (70, 130, 20)
    COLOR_SPIKES: tuple = (50, 50, 50)
    COLOR_SPRINGBOARD: tuple = ((80, 20, 20), (70, 70, 70))
    COLOR_JET: tuple = (140, 5, 180)
    COLOR_CROSSBOW: tuple = (100, 50, 0)
    COLOR_ARROW: tuple = ((80, 40, 0), (100, 100, 100), (255, 255, 255))

    TYPE_BLOCK: int = 0
    TYPE_PLAYER: int = 1
    TYPE_KEY: int = 2
    TYPE_GRAVITY_ROTATOR: int = 3
    TYPE_DOOR: int = 4
    TYPE_SPIKES: int = 5
    TYPE_SPRINGBOARD: int = 6
    TYPE_JET: int = 7
    TYPE_CROSSBOW: int = 8
    TYPE_ARROW: int = 9

    LEFT: int = -1
    RIGHT: int = 1
    UP: int = -1
    DOWN: int = 1

    sprite_arrow: pyg.Surface = None

    is_rotating: bool = False
    is_running: bool = False
    is_up_pressed: bool = False

    levels: list = []
    start_points: list = []
    current_level: int = 0
    total_keys: int = 0
    frame_count: int = 1
    frame_cycles: int = 0

    screen: pyg.Surface = None
    surface: pyg.Surface = None
    timer: pyg.time.Clock = None

    player1: player.Player = None
    opponents: dict = None

    gate: game_objects = None

    scores: dict = {}

    welcome: bool = True
    difficulty: bool = False
    score_board: bool = False
    header_font: pyg.font.Font = None
    button_font: pyg.font.Font = None

    csocket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    game_start: bool = False
    begin_cycles: int = None

    start_btn = None
    normal_btn = None
    hard_btn = None
    extreme_btn = None

    god_mode: bool = False

    class Button:
        """
        Used for easy GUI options
        Creating menus and entries
        """

        def __init__(self, pos, size, text):
            self.pos = pos
            self.size = size
            self.half = (self.size[0] / 2, self.size[1] / 2)
            self.text = text

        def render(self):
            """
            Render button to screen
            """
            Game.draw_text(self.text, self.pos, Game.button_font)
            pyg.draw.rect(Game.surface, Game.COLOR_BLACK, (self.pos[0] - self.half[0],
                                                           self.pos[1] - self.half[1],
                                                           self.size[0], self.size[1]), 4)

        def contains(self, mx, my):
            """
            Check if mouse hovers over button
            """
            return self.pos[0] - self.half[0] <= mx <= self.pos[0] + self.half[0] and \
                   self.pos[1] - self.half[1] <= my <= self.pos[1] + self.half[1]

    class Renderer(Thread):
        """
        A thread to run the render process to increase frame rate whilst keeping 60 FPS update rate
        """
        def run(self) -> None:
            """
            Render all game objects, players and menus
            """
            while Game.is_running:
                Game.surface.fill(Game.COLOR_BACKGROUND)

                # when in welcome screen
                if Game.welcome:
                    Game.draw_text(Game.TITLE, (Game.WIDTH / 2, Game.HEIGHT / 2 - 100), Game.header_font)
                    Game.start_btn.render()
                else:  # when in game screen
                    for obj in Game.get_level_objects():
                        obj.render(Game.surface, pyg)

                    for opponent in Game.opponents.values():
                        if opponent != Game.player1 and opponent.level == Game.current_level:
                            opponent.render(Game.surface, pyg)

                    Game.player1.render(Game.surface, pyg)

                    # show time since game start
                    past = Game.header_font.render(str(Game.frame_cycles), True, Game.COLOR_BLACK)
                    Game.surface.blit(past, (50, 50))

                    # if in god test mode -> show indication
                    if Game.god_mode:
                        god = Game.header_font.render('GOD', True, Game.COLOR_BLACK)
                        Game.surface.blit(god, (500, 50))

                    # in difficulty chooser
                    if Game.difficulty:
                        Game.draw_text('Choose Difficulty', (Game.WIDTH / 2, Game.HEIGHT / 2 - 200), Game.header_font)
                        Game.normal_btn.render()
                        Game.hard_btn.render()
                        Game.extreme_btn.render()

                    # in scoreboard room
                    if Game.score_board:
                        Game.draw_text('Score Board', (Game.WIDTH / 2, Game.HEIGHT / 2 - 200), Game.header_font)
                        sorted_scores = dict(sorted(Game.scores.items(), key=lambda item: item[1]))

                        off = -100
                        for key in sorted_scores.keys():
                            if sorted_scores[key] != 0:
                                Game.draw_text(key, (Game.WIDTH / 2 - 100, Game.HEIGHT / 2 + off), Game.header_font)
                                Game.draw_text(str(sorted_scores[key]),
                                               (Game.WIDTH / 2 + 100, Game.HEIGHT / 2 + off), Game.header_font)
                                off += 100

                    # when starting the game
                    if Game.game_start and Game.frame_cycles - Game.begin_cycles < 3:
                        begin_text = Game.header_font.render('Begin!', True, Game.COLOR_BLACK)
                        Game.surface.blit(begin_text, (Game.WIDTH / 2 - begin_text.get_width() / 2,
                                                       Game.HEIGHT / 2 - begin_text.get_height() / 2))

                Game.screen.blit(Game.surface, (0, 0))
                pyg.display.flip()

    class Comm(Thread):
        """
        A thread to communicate with the server and deliver messages
        """
        def run(self) -> None:
            while Game.is_running:
                msg = Game.csocket.recv(SIZE).decode()
                if msg == DIFF:  # server asking to choose difficulty
                    Game.difficulty = True
                elif msg.startswith(BEGIN):  # the game shall start
                    Game.game_start = True
                    Game.begin_cycles = Game.frame_cycles
                    Game.csocket.send(ACK.encode())
                    Game.next_level()  # exit lobby level
                    Game.levels = Game.levels[:int(msg.split(':')[1]) + 2]  # adjust level amount to difficulty
                elif msg.startswith(SCORE):  # receive scores to show on leaderboard
                    msg_split = msg.split(':')[1:]
                    for i in range(0, len(msg_split) - 1, 2):
                        if msg_split[i] != Game.player1.color:
                            Game.scores[msg_split[i]] = int(msg_split[i + 1])

                    Game.csocket.send(f'{Game.frame_cycles}'.encode())
                elif msg.startswith(POS):  # receive position of other players
                    dic = {}
                    data = msg.split(':')[1:]
                    for i in range(0, len(data) - 1, 2):
                        data_list = data[i + 1][1:-1].split(', ')
                        dic[data[i]] = (int(data_list[0]), float(data_list[1]), float(data_list[2]))

                    for color in dic.keys():
                        if Game.opponents[color] != Game.player1:
                            Game.opponents[color].level = dic[color][0]
                            Game.opponents[color].x = dic[color][1]
                            Game.opponents[color].y = dic[color][2]

                    # when in scoreboard room, send indication and current position for shared lounge effect
                    if Game.current_level == len(Game.levels) - 1:
                        Game.csocket.send(f'{DONE}:{Game.current_level}:{Game.player1.x}:{Game.player1.y}'.encode())
                        for p in Game.opponents.keys():
                            if Game.opponents[p] == Game.player1:
                                Game.scores[p] = Game.frame_cycles
                                break
                    else:  # send current position in level to other players
                        Game.csocket.send(f'{Game.current_level}:{Game.player1.x}:{Game.player1.y}'.encode())

            Game.csocket.send(QUIT.encode())

    @staticmethod
    def draw_text(text, pos, font):
        """
        Draw centered text to surface
        """
        button_text = font.render(text, True, Game.COLOR_BLACK)
        Game.surface.blit(button_text, (pos[0] - button_text.get_width() / 2,
                                        pos[1] - button_text.get_height() / 2))

    @staticmethod
    def initialize() -> None:
        """
        Initialize elements and libraries
        """
        pyg.init()
        pyg.font.init()

        Game.header_font = pyg.font.SysFont('Consolas', 40)
        Game.button_font = pyg.font.SysFont('Consolas', 25)

        pyg.display.set_caption(Game.TITLE)
        pyg.display.gl_set_attribute(pyg.GL_MULTISAMPLEBUFFERS, 2)

        Game.screen = pyg.display.set_mode((Game.WIDTH, Game.HEIGHT))
        Game.surface = pyg.Surface((Game.WIDTH, Game.HEIGHT))
        Game.surface.fill(Game.COLOR_BACKGROUND)

        Game.timer = pyg.time.Clock()

        Game.sprite_arrow = pyg.image.load('assets/arrow.png')

        Game.generate_levels()
        Game.init_level()

        Game.opponents = {
            PURPLE: player.Player(Game.COLOR_PLAYER_PURPLE),
            RED: player.Player(Game.COLOR_PLAYER_RED),
            GREEN: player.Player(Game.COLOR_PLAYER_GREEN),
            BROWN: player.Player(Game.COLOR_PLAYER_BROWN)
        }

        Game.start_btn = Game.Button((Game.WIDTH / 2, Game.HEIGHT / 2), (200, 50), 'START')

        Game.normal_btn = Game.Button((Game.WIDTH / 2, Game.HEIGHT / 2 - 100), (200, 50), 'NORMAL')
        Game.hard_btn = Game.Button((Game.WIDTH / 2, Game.HEIGHT / 2), (200, 50), 'HARD')
        Game.extreme_btn = Game.Button((Game.WIDTH / 2, Game.HEIGHT / 2 + 100), (200, 50), 'EXTREME')

    @staticmethod
    def rotate(rd: int) -> None:
        """
        Rotate the level
        """
        Game.is_rotating = True

        for b in Game.get_level_objects():
            b.rotate_gravity(rd)

    @staticmethod
    def stop_rotation() -> None:
        """
        Stop rotating the level
        """
        Game.is_rotating = False

    @staticmethod
    def run() -> None:
        """
        Run the main game loop
        """
        Game.is_running = True

        Game.Renderer().start()

        while Game.is_running:
            if Game.welcome:  # welcome screen
                Game.observe_welcome_events()
                continue
            else:  # game screen
                Game.observe_events()

            Game.timer.tick(Game.FPS)

            if Game.is_up_pressed:
                Game.player1.jump()

            Game.update_objects()

            # track time
            if Game.game_start and not Game.score_board:
                Game.frame_count += 1
                if Game.frame_count >= 61:
                    Game.frame_count = 1
                    Game.frame_cycles += 1

        pyg.quit()
        sys.exit(0)

    @staticmethod
    def stop_running() -> None:
        Game.is_running = False

    @staticmethod
    def observe_welcome_events() -> None:
        """
        Catch events on the welcome screen
        """
        for e in pyg.event.get():
            if e.type == pyg.QUIT:
                Game.stop_running()
                continue

            if e.type == pyg.MOUSEBUTTONDOWN:
                mx, my = pyg.mouse.get_pos()
                if Game.start_btn.contains(mx, my):
                    Game.csocket.connect(IP)
                    color = Game.csocket.recv(SIZE).decode()
                    Game.player1 = Game.opponents[color]
                    Game.csocket.send(ACK.encode())
                    Game.Comm().start()
                    Game.welcome = False

    @staticmethod
    def observe_events() -> None:
        """
        Catch events on game screen
        """
        for e in pyg.event.get():
            if e.type == pyg.QUIT:
                Game.stop_running()
                continue

            if e.type == pyg.KEYDOWN:
                if e.key == pyg.K_LEFT:
                    Game.player1.start_left()
                if e.key == pyg.K_RIGHT:
                    Game.player1.start_right()
                if e.key == pyg.K_UP:
                    if Game.player1.is_standing:
                        Game.is_up_pressed = True

            if e.type == pyg.KEYUP:
                if e.key == pyg.K_LEFT:
                    Game.player1.stop_left()
                if e.key == pyg.K_RIGHT:
                    Game.player1.stop_right()
                if e.key == pyg.K_UP:
                    Game.is_up_pressed = False
                if e.key == pyg.K_r:
                    Game.player1.die()
                if e.key == pyg.K_ESCAPE:
                    Game.stop_running()
                    continue
                if e.key == pyg.K_g:
                    Game.god_mode = not Game.god_mode

            if e.type == pyg.MOUSEBUTTONDOWN and Game.difficulty:
                mx, my = pyg.mouse.get_pos()
                if Game.normal_btn.contains(mx, my):
                    Game.csocket.send(NORMAL.encode())
                    Game.difficulty = False
                elif Game.hard_btn.contains(mx, my):
                    Game.csocket.send(HARD.encode())
                    Game.difficulty = False
                elif Game.extreme_btn.contains(mx, my):
                    Game.csocket.send(EXTREME.encode())
                    Game.difficulty = False

    @staticmethod
    def update_objects() -> None:
        """
        Update all game objects in level
        """
        Game.player1.fall()
        Game.player1.update()

        if not Game.game_start:
            for opponent in Game.opponents.values():
                if opponent != Game.player1:
                    opponent.fall()
                    opponent.update()

        if not Game.player1.is_alive:
            Game.generate_levels()
            Game.init_level()
            Game.player1.is_alive = True
            return

        if Game.player1.total_keys_collected >= Game.total_keys:
            if not Game.gate.is_animating_closure:
                Game.gate.open()

            if Game.player1.passed():
                Game.next_level()

        for obj in Game.get_level_objects():
            obj.update()

    @staticmethod
    def add_level(lvl: tuple) -> None:
        Game.levels.append(lvl)

    @staticmethod
    def new_start_point(x: float, y: float) -> None:
        Game.start_points.append((x, y))

    @staticmethod
    def next_level() -> None:
        """
        Transition to the next level
        """
        obstacles.Crossbow.count = 0
        Game.current_level += 1
        Game.init_level()
        Game.player1.reset()

        if Game.current_level == len(Game.levels) - 1:
            Game.score_board = True

    @staticmethod
    def get_level_objects() -> tuple:
        return Game.levels[Game.current_level]

    @staticmethod
    def generate_levels() -> None:
        """
        Build and list all levels in the game
        Lobby: 0
        Normal: 1st -> 3rd
        Hard: 1st -> 5th
        Extreme: 1st -> 6th
        Score Lounge: 7th
        """
        Game.levels.clear()

        # Limbo
        level = (
            game_objects.Block(0, 590, 590, 10),
            game_objects.Block(10, 0, 590, 10),
            game_objects.Block(0, 0, 10, 590),
            game_objects.Block(590, 10, 10, 590),
            game_objects.Block(120, 370, 50, 50),
            game_objects.Block(280, 340, 150, 40),
            game_objects.Block(200, 187, 20, 20),
            game_objects.Block(10, 100, 150, 20),
            game_objects.Block(10, 490, 50, 100),
            game_objects.Block(490, 294, 100, 20),
            game_objects.Block(280, 290, 50, 50),
            game_objects.Door(-100, 0),
        )
        Game.new_start_point(413, 465)
        Game.add_level(level)

        # 1st Level - Normal
        level = (
            game_objects.Block(0, 590, 590, 10),
            game_objects.Block(10, 0, 590, 10),
            game_objects.Block(0, 100, 10, 490),
            game_objects.Block(590, 10, 10, 590),
            game_objects.Block(120, 370, 50, 50),
            game_objects.Block(280, 340, 150, 40),
            game_objects.Block(200, 187, 20, 20),
            game_objects.Block(10, 100, 150, 20),
            game_objects.Door(0, 0),
            game_objects.Block(10, 490, 50, 100),
            game_objects.Block(490, 294, 100, 20),
            power_ups.Key(538, 237),
            game_objects.Block(280, 290, 50, 50)
        )
        Game.new_start_point(413, 465)
        Game.add_level(level)

        # 2nd Level - Normal
        level = (
            game_objects.Block(0, 0, 600, 10),
            game_objects.Block(0, 10, 10, 600),
            game_objects.Block(10, 590, 590, 10),
            game_objects.Block(590, 110, 10, 480),
            game_objects.Door(590, 10),
            power_ups.Key(197, 461),
            power_ups.Key(415, 302),
            power_ups.Key(272, 116),
            power_ups.Key(445, 62),
            power_ups.Jet(280, 206),
            obstacles.Crossbow(550, 300, -1, 0),
            game_objects.Block(375, 338, 100, 10),
            game_objects.Block(240, 238, 100, 10),
            game_objects.SpringBoard(250, 570)
        )
        Game.new_start_point(40, 530)
        Game.add_level(level)

        # 3rd level - Normal
        level = (
            game_objects.Block(0, 590, 590, 10),
            game_objects.Block(0, 0, 10, 590),
            game_objects.Block(10, 0, 590, 10),
            game_objects.Door(590, 10),
            obstacles.Spikes(10, 10, 10, 580, 1),
            obstacles.Spikes(100, 80, 10, 510, -1),
            obstacles.Spikes(110, 70, 180, 10, -1),
            obstacles.Spikes(290, 80, 10, 510, 1),
            obstacles.Spikes(380, 10, 10, 340, -1),
            game_objects.SpringBoard(20, 570),
            obstacles.Spikes(390, 10, 10, 340, 1),
            obstacles.Spikes(490, 150, 50, 10, -1),
            obstacles.Spikes(480, 160, 10, 430, -1),
            game_objects.Block(590, 110, 10, 490),
            power_ups.Jet(50, 98),
            power_ups.Key(50, 33),
            power_ups.Key(325, 36),
            power_ups.Key(380, 464),
            game_objects.SpringBoard(310, 570),
            game_objects.SpringBoard(390, 570),
            power_ups.Key(489, 69),
            game_objects.Block(110, 80, 180, 510),
            game_objects.Block(490, 160, 100, 430)
        )
        Game.new_start_point(40, 300)
        Game.add_level(level)

        # 4th level - Hard
        level = (
            game_objects.Block(0, 590, 600, 10),
            game_objects.Block(0, 10, 10, 590),
            game_objects.Block(0, 0, 600, 10),
            game_objects.Block(590, 0, 10, 490),
            obstacles.Crossbow(510, 10, 0, 1),
            power_ups.Jet(83, 380),
            game_objects.SpringBoard(509, 570),
            obstacles.Spikes(158, 332, 265, 257, -1),
            game_objects.SpringBoard(428, 570),
            game_objects.Block(540, 490, 50, 20),
            game_objects.Door(590, 490),
            obstacles.Spikes(542, 480, 50, 10, -1),
            power_ups.Key(555, 344)
        )
        Game.new_start_point(46, 550)
        Game.add_level(level)

        # 5th level - Hard
        level = (
            game_objects.Block(0, 590, 600, 120),
            game_objects.Block(590, 0, 10, 250),
            game_objects.Block(0, 0, 600, 10),
            game_objects.Block(0, 0, 10, 590),
            game_objects.Block(469, 469, 10, 121),
            game_objects.Block(121, 469, 10, 121),
            obstacles.Crossbow(111, 10, 0, 1),
            game_objects.Block(540, 165, 50, 10),
            game_objects.Block(10, 165, 60, 10),
            game_objects.Block(10, 425, 60, 10),
            game_objects.Block(540, 425, 50, 10),
            game_objects.Block(469, 10, 10, 121),
            game_objects.Block(142, 10, 10, 121),
            obstacles.Crossbow(10, 135, 1, 0),
            power_ups.Key(50, 50),
            power_ups.Key(530, 50),
            game_objects.SpringBoard(389, 570),
            game_objects.SpringBoard(132, 570),
            game_objects.Block(590, 350, 10, 250),
            game_objects.Door(590, 250)
        )
        Game.new_start_point(280, 550)
        Game.add_level(level)

        # 6th level - Extreme
        level = (
            game_objects.Block(0, 590, 600, 10),
            game_objects.Block(0, 0, 600, 10),
            game_objects.Block(0, 10, 10, 590),
            game_objects.Block(590, 0, 10, 500),
            game_objects.Block(430, 488, 10, 10),
            game_objects.Door(430, 385),
            game_objects.Block(430, 286, 160, 10),
            game_objects.Block(549, 402, 41, 10),
            game_objects.SpringBoard(337, 569),
            obstacles.Spikes(11, 579, 540, 10, -1),
            obstacles.Spikes(430, 275, 152, 10, -1),
            obstacles.Spikes(579, 11, 10, 255, 0),
            obstacles.Spikes(519, 80, 10, 107, 1),
            obstacles.Spikes(469, 190, 49, 10, 1),
            obstacles.Spikes(469, 70, 49, 10, -1),
            obstacles.Spikes(459, 80, 10, 107, -1),
            power_ups.Key(538, 234),
            power_ups.Key(495, 26),
            power_ups.Jet(473, 232),
            game_objects.Block(215, 544, 10, 10),
            game_objects.Block(430, 286, 10, 96)
        )
        Game.new_start_point(200, 503)
        Game.add_level(level)

        # Score board
        level = (
            game_objects.Block(0, 0, 590, 10),
            game_objects.Block(590, 0, 10, 590),
            game_objects.Block(10, 590, 590, 10),
            game_objects.Block(0, 10, 10, 590)
        )
        Game.new_start_point(122, 445)
        Game.add_level(level)

    @staticmethod
    def init_level() -> None:
        """
        Initialize keys for current level
        """
        Game.total_keys *= 0 if Game.total_keys != 0 else 1

        for obj in Game.get_level_objects():
            if obj.type == Game.TYPE_KEY:
                Game.total_keys += 1
            elif obj.type == Game.TYPE_DOOR:
                Game.gate = obj
