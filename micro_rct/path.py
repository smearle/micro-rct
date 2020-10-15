from collections import defaultdict
import random
import numpy as np
import copy
from .tilemap import Map

class Path:
    GRASS = 0
    PATH = 1
    VOMIT = 2

    def __repr__(self):
        return 'Path at {}'.format(self.position)

    def __init__(self, position, path_map, path_net=None, is_entrance=False):
        self.name = 'path'
       #self.path_net = path_net
        self.position = position
        self.entrance = position
        self.path_map = path_map
        self.links = []
        self.is_entrance = is_entrance
        assert pos_in_map(position, path_map)

    def clone(self):
        new_path_map = self.path_map.copy()
        new_path = Path(self.position, new_path_map)
        return new_path

    def get_connecting(self, path_net):
        self.west = self.get_adjacent((-1, 0), path_net)
        self.north = self.get_adjacent((0, 1), path_net)
        self.east = self.get_adjacent((1, 0), path_net)
        self.south = self.get_adjacent((0, -1), path_net)
        self.links = [self.west, self.north, self.east, self.south]
        connections = 0
        for l in self.links:
            if l:
                connections += 1
        if connections > 2:
            self.junction = True
        else:
            self.junction = False

    def get_adjacent(self, direction, path_net):
        adj_pos = (self.position[0] + direction[0],
                   self.position[1] + direction[1],
                   )
        # FIXME store dict of whether paths have been connected
        if adj_pos in path_net:
            adj_path = path_net[adj_pos]
            if not (adj_path.is_entrance and self.is_entrance):
                return adj_pos
        elif pos_in_map(adj_pos, self.path_map) and self.path_map[adj_pos] >0:
            return adj_pos
        return adj_pos

def pos_in_map(pos, mp):
    return 0 <= pos[0] < mp.shape[0] and 0 <= pos[1] < mp.shape[1]
