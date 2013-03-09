#!/usr/bin/env python3
# -*-coding:Utf-8 -*
import socket
import json
from game import Game, Map
from game.map import Base, Mine

def send_json(socket, obj):
    socket.sendall(bytes(json.dumps(obj) + '\n', 'UTF-8'))

def recv_json(socket):
    if not hasattr(recv_json, 'files'):
        recv_json.files = {} # static variable

    if not socket in recv_json.files:
        recv_json.files[socket] = socket.makefile()

    data = recv_json.files[socket].readline()
    return json.loads(data.strip())

class BaseBot:
    def __init__(self, host, port, username):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

        send_json(self.socket, {
            'type': 'player',
            'name': username,
        })

        assert recv_json(self.socket) == True

    def run(self):
        result = recv_json(self.socket)
        self.team_id = int(result['id'])
        self.players = result['players']
        self.game = Game(Map(size=result['map_size']))

        while not self.game.winner():
            # waiting
            result = recv_json(self.socket)
            self.game.set_state(result)

            # computing turn
            self.init_turn()
            self.compute_turn()
            self.end_turn()

        if self.game.winner() == self.team_id:
            print('You win !')
        else:
            print('You lost.')

    def init_turn(self):
        self.commands = []
        self.units_moved = set()

        # computed only the first time
        if not hasattr(self, 'base_pos'):
            for pos, building in self.game.map.iter_buildings():
                if isinstance(building, Base) and building.team == self.team_id:
                    self.base_pos = pos

        if not hasattr(self, 'mines_pos'):
            self.mines_pos = []

            for pos, building in self.game.map.iter_buildings():
                if isinstance(building, Mine):
                    self.mines_pos.append(pos)

    def end_turn(self):
        send_json(self.socket, self.commands)

    def move_unit(self, from_, to):
        unit = self.game.map.units[from_]
        assert unit
        assert unit.team == self.team_id
        assert unit not in self.units_moved

        command = {
            'type': 'move',
            'from': from_,
            'to': to,
        }
        self.game.play_turn(self.team_id, [command])
        self.commands.append(command)
        self.units_moved.add(unit)

    def create_unit(self):
        assert self.base().gold > 0
        assert not self.game.map.units[self.base_pos]

        command = {
            'type': 'create',
            'pos': self.base_pos,
        }
        self.game.play_turn(self.team_id, [command])
        self.commands.append(command)
        self.units_moved.add(self.game.map.units[self.base_pos])

    def base(self):
        return self.game.map.ground[self.base_pos]

    def compute_turn(self):
        pass
