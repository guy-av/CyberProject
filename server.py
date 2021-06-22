import random
import socket
import threading


def thread(function):
    return threading.Thread(target=function)


class Player:
    def __init__(self, csocket, color):
        self.socket = csocket
        self.color = color
        self.score = 0

        self.send(f'{self.color}')
        self.recv()  # ACK

    def begin(self):
        self.send('BEGIN')
        self.recv()  # ACK

    def send(self, msg):
        self.socket.send(msg.encode())

    def recv(self, size=1024):
        return self.socket.recv(size).decode()


class Server:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('0.0.0.0', 8080))
        self.socket.listen()

        self.rooms = [Room()]

    def run(self):
        while True:
            client, _ = self.socket.accept()

            if self.current().is_full():
                self.rooms.append(Room())

            self.current().add_player(client)

    def current(self):
        return self.rooms[-1]


class Room(threading.Thread):
    def __init__(self):
        super().__init__()

        self.difficulty = 4
        self.players = []
        self.colors = ['Purple', 'Red', 'Green', 'Brown']
        random.shuffle(self.colors)

        self.positions = {
            'Purple': (0, .0, .0),  # (level, x, y)
            'Red': (0, .0, .0),
            'Green': (0, .0, .0),
            'Brown': (0, .0, .0)
        }

        self.scores = {
            'Purple': 0,
            'Red': 0,
            'Green': 0,
            'Brown': 0
        }

    def play(self):
        threads = []
        for player in self.players:
            ct = thread(lambda: self.track_player(player))
            threads.append(ct)
            ct.start()

        while True:
            if all([not t.is_alive() for t in threads]):
                break

    def run(self):
        self.players[0].send('DIFF')
        self.difficulty = int(self.players[0].recv())
        self.play()

    def track_player(self, player):
        player.begin()

        while True:
            player.send('DATA')
            data = player.recv()

            if data.startswith('DONE'):
                player.send('SCORE')
                score = int(player.recv())

                self.scores[player.color] = score
                continue

            data_list = data.split(':')
            self.positions[player.color] = (int(data_list[0]), float(data_list[1]), float(data_list[2]))

            pos_msg = ''
            for key in self.positions.keys():
                pos_msg += f':{key}:{self.positions[key]}'
            player.send(pos_msg[1:])
            player.recv()  # ACK

    def add_player(self, csocket):
        self.players.append(Player(csocket, self.colors[len(self.players) - 1]))
        if self.is_full():
            self.start()

    def is_full(self):
        return len(self.players) == 4


if __name__ == '__main__':
    Server().run()
