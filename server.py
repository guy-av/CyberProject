import random
import socket
import threading

from consts import *


def thread(function):
    return threading.Thread(target=function)


class Player:
    """
    Simplify interaction with player client
    """
    def __init__(self, csocket, color):
        self.socket = csocket
        self.color = color
        self.score = 0

        self.send(f'{self.color}')
        self.recv()  # ACK

    def begin(self, level):
        self.send(f'{BEGIN}:{level}')
        self.recv()  # ACK

    def send(self, msg):
        self.socket.send(msg.encode())

    def recv(self, size=1024):
        return self.socket.recv(size).decode()


class Server:
    """
    Accept players and direct to rooms
    """
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(ADDRESS)
        self.socket.listen()

        self.rooms = [Room()]

    def run(self):
        """
        Accept and connect players to rooms
        """
        while True:
            client, _ = self.socket.accept()

            if self.current().is_full():
                self.rooms.append(Room())

            self.current().add_player(client)

    def current(self):
        return self.rooms[-1]


class Room(threading.Thread):
    """
    Interacts with all four players to ensure everyone gets data
    """
    def __init__(self):
        super().__init__()

        self.difficulty = 4
        self.players = []
        self.colors = [PURPLE, RED, GREEN, BROWN]
        random.shuffle(self.colors)

        self.positions = {
            PURPLE: (0, .0, .0),  # (level, x, y)
            RED: (0, .0, .0),
            GREEN: (0, .0, .0),
            BROWN: (0, .0, .0)
        }

        self.scores = {
            PURPLE: 0,
            RED: 0,
            GREEN: 0,
            BROWN: 0
        }

    def run(self):
        """
        Request difficulty and start game
        """
        self.players[0].send(DIFF)
        self.difficulty = int(self.players[0].recv())
        self.play()

    def play(self):
        """
        Start threads for players, then wait for them to finish
        """
        threads = []
        for player in self.players:
            ct = thread(lambda: self.track_player(player))
            threads.append(ct)
            ct.start()

        while True:
            if all([not t.is_alive() for t in threads]):
                break

    def track_player(self, player):
        """
        Communicate with specific player (threaded)
        """
        player.begin(self.difficulty)

        while True:
            try:
                # compose a message containing all positions of players
                pos_msg = ''
                for key in self.positions.keys():
                    pos_msg += f':{key}:{self.positions[key]}'
                player.send(f'{POS}{pos_msg}')
                data = player.recv()

                if data.startswith(DONE):
                    # compose a message containing all scores of players
                    score_msg = ''
                    for key in self.scores.keys():
                        score_msg += f':{key}:{self.scores[key]}'
                    player.send(f'{SCORE}{score_msg}')
                    score = int(player.recv())

                    # receive player score and location in lounge
                    self.scores[player.color] = score
                    split = data.split(':')[1:]
                    self.positions[player.color] = (int(split[0]), float(split[1]), float(split[2]))
                    continue
                elif QUIT in data:
                    player.socket.close()
                    break

                # update positions
                data_list = data.split(':')
                self.positions[player.color] = (int(data_list[0]), float(data_list[1]), float(data_list[2]))
            except socket.error:
                pass

    def add_player(self, csocket):
        """
        Add a player to the room
        """
        self.players.append(Player(csocket, self.colors[len(self.players) - 1]))
        if self.is_full():
            self.start()

    def is_full(self):
        return len(self.players) == 4


if __name__ == '__main__':
    Server().run()
