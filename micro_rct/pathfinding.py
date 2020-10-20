
from collections import defaultdict
import random
import numpy as np
import copy
from .tilemap import Map

# For debugging pathfinding only
#import cv2


class PathFinder:
    adj = [(0, 1), (-1, 0), (1, 0), (0, -1)]
    def __init__(self, path_net):
        self.maxCounter = 100
        #guest path finding line 1172, orignal is 15000 for guest I don't know why 15000
        self.maxTilesChecked = -1
        self.checked = defaultdict(int) #key: (x,y)  val: score #lower is better
        # since we only consider 'checked' once score is returned
        self.checking = {}
        # maxpeepPathFindJunctions = 0
        self.availablePath = None
        self.goal = (0,0)
        self.start = (0,0)
        self.path_net = path_net
       #cv2.namedWindow("pathfinder checking", cv2.WINDOW_NORMAL)
       #cv2.namedWindow("pathfinder checked", cv2.WINDOW_NORMAL)

    def clone(self):
        new_path_net = {}

        for pos, path in self.path_net.items():
            new_path = path.clone()
            new_path_net[pos] = new_path
        new_path_finder = PathFinder(new_path_net)

        return new_path_finder

    def peep_find(self, peep, park):
        trg = peep.headingTo.entrance
        src = peep.position

        return self.find_node(park, src, trg)

    def find_node(self, park, src, trg):
        ''' this uses node objects that are connected to one another, i.e., searching a graph'''
        path_net = park.path_net
        self.maxTilesChecked = len(path_net)
        self.counter = self.maxCounter
        checked = {}
        checking = []
        pos_to_routes = {}
        checking.append(src)
        pos_to_routes[src] = []
       #print('peep heading to {}'.format(self.goal))
       #assert self.goal in path_net
        if trg not in path_net:
            print('goal not in path net:', trg)
            raise Exception
            return -1
        # if the peep is off the path...

        if src not in path_net:
            return [src]

        i = 0
        while checking:
            # depth-first search
            curr = checking.pop(0)
            if curr == trg:
                # return first route to goal
                return pos_to_routes[curr]
            assert curr in path_net
            path = path_net[curr]
            for next_pos in path.links:
                # get children
                if next_pos in path_net and next_pos not in checking and not next_pos in checked:
                   #print(path_net)
                    checking.append(next_pos)
                    pos_to_routes[next_pos] = [pos for pos in pos_to_routes[curr]] + [next_pos]

            checked[curr] = len(pos_to_routes[curr]) + self.heuristic_from_goal(curr)
            i += 1

        best_pos = sorted([(pos, score) for (pos, score) in checked.items()], key=lambda pos_score:pos_score[1])[0][0]
        route = pos_to_routes[best_pos]
            
        return route

    def find_map(self, map_arr, src, trg):
        ''' this searches over an array '''
        self.goal = trg
        self.counter = self.maxCounter
        self.checked = {}
        checking = []
        link_scores = []
        pos_to_routes = {}
        checking.append(src)
        pos_to_routes[src] = []

        i = 0
        while checking:
            curr = checking[0]

            if i > 1 and map_arr[Map.PATH, curr[0], curr[1]] != -1:
                self.checked[curr] = 0

                return pos_to_routes[curr]

            for adj in self.adj:
                next_pos = (curr[0] + adj[0], curr[1] + adj[1])
                # next tile cannot be out of bounds, cannot be a ride unless the target entrance

                if (next_pos not in checking) and (next_pos not in self.checked) and \
                0 <= next_pos[0] < map_arr.shape[1] and 0 <= next_pos[1] < map_arr.shape[2] \
                and (map_arr[Map.RIDE, next_pos[0], next_pos[1]] == -1 or \
                        (map_arr[Map.PATH, next_pos[0], next_pos[1]] != -1 and next_pos == trg)):
                    checking.append(next_pos)
                    pos_to_routes[next_pos] = [pos for pos in pos_to_routes[curr]] + [next_pos]
            self.checked[curr] = len(pos_to_routes[curr]) + self.heuristic_from_goal(curr)
           #self.checked[curr] = float('inf')
            checking.pop(0)
            i += 1

        best_pos = sorted([(pos, score) for (pos, score) in self.checked.items()], key=lambda pos_score:pos_score[1])[0][0]
        route = pos_to_routes[best_pos]
       #print('settling for heuristic solution {} while attempting to link {} and {}'.format(route, src, trg))
       #print(map_arr[Map.RIDE])
        return route



    def heuristic_from_goal(self, pos:tuple):
        goal = self.goal

        return abs(pos[0]-goal[0])+abs(pos[1]-goal[1])
