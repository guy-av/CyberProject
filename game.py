import json
import socket
import sys
from threading import Thread

import pygame as pyg

import game_objects
import obstacles
import player
import power_ups


class Game:
    WIDTH: int = 600
    HEIGHT: int = 600
    GRAVITY: float = 0.3
    FPS: int = 60
    TITLE: str = 'Box Ninja'

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

    welcome: bool = True
    header: pyg.font.Font = None
    button: pyg.font.Font = None
    button_rect: tuple = (WIDTH // 2 - 100, HEIGHT // 2 - 25, 200, 50)

    csocket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    game_start: bool = False
    begin_cycles: int = None

    class Renderer(Thread):
        def run(self) -> None:
            while Game.is_running:
                Game.surface.fill(Game.COLOR_BACKGROUND)

                if Game.welcome:
                    header_text = Game.header.render('Dyber', True, Game.COLOR_BLACK)
                    Game.surface.blit(header_text, (Game.WIDTH / 2 - header_text.get_width() / 2,
                                                    Game.HEIGHT / 2 - 100))

                    pyg.draw.rect(Game.surface, Game.COLOR_BLACK, Game.button_rect, 4)

                    button_text = Game.button.render('START', True, Game.COLOR_BLACK)
                    Game.surface.blit(button_text, (Game.WIDTH / 2 - button_text.get_width() / 2,
                                                    Game.HEIGHT / 2 - button_text.get_height() / 2))
                else:
                    for obj in Game.get_level_objects():
                        obj.render(Game.surface, pyg)

                    for opponent in Game.opponents.values():
                        if opponent != Game.player1 and opponent.level == Game.current_level:
                            opponent.render(Game.surface, pyg)

                    Game.player1.render(Game.surface, pyg)

                    past = Game.header.render(str(Game.frame_cycles), True, Game.COLOR_BLACK)
                    Game.surface.blit(past, (50, 50))

                    if Game.game_start and Game.frame_cycles - Game.begin_cycles < 3:
                        begin_text = Game.header.render('Begin!', True, Game.COLOR_BLACK)
                        Game.surface.blit(begin_text, (Game.WIDTH / 2 - begin_text.get_width() / 2,
                                                 Game.HEIGHT / 2 - begin_text.get_height() / 2))

                Game.screen.blit(Game.surface, (0, 0))
                pyg.display.flip()

    class Comm(Thread):
        def run(self) -> None:
            while Game.is_running:
                msg = Game.csocket.recv(1024).decode()
                if msg == 'DIFF':
                    Game.csocket.send('4'.encode())
                elif msg == 'DATA':
                    Game.csocket.send(f'{Game.current_level}:{Game.player1.x}:{Game.player1.y}'.encode())
                elif msg == 'BEGIN':
                    Game.game_start = True
                    Game.begin_cycles = Game.frame_cycles
                    Game.csocket.send('ACK'.encode())
                else:
                    dic = {}
                    data = msg.split(':')
                    for i in range(0, len(data) - 1, 2):
                        data_list = data[i + 1][1:-1].split(', ')
                        dic[data[i]] = (int(data_list[0]), float(data_list[1]), float(data_list[2]))

                    for color in dic.keys():
                        if Game.opponents[color] != Game.player1:
                            Game.opponents[color].level = dic[color][0]
                            Game.opponents[color].x = dic[color][1]
                            Game.opponents[color].y = dic[color][2]

                    Game.csocket.send('ACK'.encode())

                # for color in data.keys():
                #     Game.opponents[color].x = data[color][0]

    @staticmethod
    def initialize() -> None:
        pyg.init()
        pyg.font.init()

        Game.header = pyg.font.SysFont('Consolas', 40)
        Game.button = pyg.font.SysFont('Consolas', 25)

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
            'Purple': player.Player(Game.COLOR_PLAYER_PURPLE),
            'Red': player.Player(Game.COLOR_PLAYER_RED),
            'Green': player.Player(Game.COLOR_PLAYER_GREEN),
            'Brown': player.Player(Game.COLOR_PLAYER_BROWN)
        }

    @staticmethod
    def rotate(rd: int) -> None:
        Game.is_rotating = True

        for b in Game.get_level_objects():
            b.rotate_gravity(rd)

    @staticmethod
    def stop_rotation() -> None:
        Game.is_rotating = False

    @staticmethod
    def run() -> None:
        Game.is_running = True

        Game.Renderer().start()

        while Game.is_running:
            if Game.welcome:
                Game.observe_welcome_events()
                continue
            else:
                Game.observe_events()

            Game.timer.tick(Game.FPS)

            if Game.is_up_pressed:
                Game.player1.jump()

            Game.update_objects()

            if Game.game_start:
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
        for e in pyg.event.get():
            if e.type == pyg.QUIT:
                Game.stop_running()
                continue

            if e.type == pyg.MOUSEBUTTONDOWN:
                mx, my = pyg.mouse.get_pos()
                if Game.button_rect[0] < mx < Game.button_rect[0] + Game.button_rect[2] and \
                        Game.button_rect[1] < my < Game.button_rect[1] + Game.button_rect[3]:
                    Game.csocket.connect(('127.0.0.1', 8080))
                    color = Game.csocket.recv(1024).decode()
                    Game.player1 = Game.opponents[color]
                    Game.csocket.send('ACK'.encode())
                    Game.Comm().start()
                    Game.welcome = False

    @staticmethod
    def observe_events() -> None:
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

    @staticmethod
    def update_objects() -> None:
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
    def add_level(l: tuple) -> None:
        Game.levels.append(l)

    @staticmethod
    def new_start_point(x: float, y: float) -> None:
        Game.start_points.append((x, y))

    @staticmethod
    def next_level() -> None:
        if Game.current_level + 1 == len(Game.levels):
            Game.stop_running()
            print('congratulations.')
        else:
            obstacles.Crossbow.count = 0
            Game.current_level += 1
            Game.init_level()
            Game.player1.reset()

    @staticmethod
    def get_level_objects() -> tuple:
        return Game.levels[Game.current_level]

    @staticmethod
    def generate_levels() -> None:
        Game.levels.clear()

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

        level = (
            power_ups.Key(400, 400),
            game_objects.Door(590, 490),
            game_objects.Block(0, 0, 10, 590),
            game_objects.Block(0, 590, 600, 10),
            game_objects.Block(10, 0, 590, 10),
            game_objects.Block(590, 10, 10, 480),
            game_objects.SpringBoard(Game.WIDTH / 2, 570)
        )
        Game.new_start_point(50, 50)
        Game.add_level(level)

        level = (
            game_objects.Door(0, 490),
            game_objects.Block(590, 10, 10, 590),
            game_objects.Block(0, 590, 590, 10),
            game_objects.Block(10, 0, 590, 10),
            game_objects.Block(0, 0, 10, 490),
            obstacles.Spikes(10, 300, 10, 100, 1),
            power_ups.GravityRotator(474, 539, -1),
            power_ups.Key(531, 541),
            power_ups.GravityRotator(517, 162, -1),
            power_ups.Key(372, 98),
            power_ups.GravityRotator(280, 105, -1),
            power_ups.Key(66, 192)
        )
        Game.new_start_point(60, 530)
        Game.add_level(level)

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

        level = (
            game_objects.Block(150, 470, 200, 10),
            game_objects.Block(510, 310, 66, 151),
            game_objects.Block(425, 310, 88, 58),
            game_objects.Block(425, 415, 92, 50),
            game_objects.Block(0, 590, 600, 10),
            game_objects.Block(0, 0, 10, 590),
            game_objects.Block(10, 0, 590, 10),
            game_objects.Block(590, 200, 10, 390),
            game_objects.Block(590, 10, 10, 90),
            game_objects.Block(510, 275, 50, 50),
            power_ups.Jet(405, 380),
            power_ups.Key(90, 380),
            power_ups.Key(370, 155),
            power_ups.GravityRotator(505, 315, 1),
            obstacles.Spikes(150, 580, 430, 10, -1),
            obstacles.Crossbow(460, 375, -1, 0),
            game_objects.SpringBoard(60, 570),
            game_objects.Door(590, 100)
        )
        Game.new_start_point(15, 545)
        Game.add_level(level)

    @staticmethod
    def init_level() -> None:
        Game.total_keys *= 0 if Game.total_keys != 0 else 1

        for obj in Game.get_level_objects():
            if obj.type == Game.TYPE_KEY:
                Game.total_keys += 1
            elif obj.type == Game.TYPE_DOOR:
                Game.gate = obj
