from collections import defaultdict
import numpy as np
import copy
from .tilemap import Map
# For debugging pathfinding only
#import cv2


class PathFinder:
    adj = [(0,-1), (-1, 0), (1, 0), (0, 1)]
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

    def peep_find(self, peep):
        park = peep.park
        trg = peep.headingTo.entrance
        src = peep.position
        return self.find_node(park, src, trg)

    def find_node(self, park, src, trg):
        ''' this uses node objects that are connected to one another, i.e., searching a graph'''
        self.goal = trg
        path_net = park.path_net
        self.maxTilesChecked = len(path_net)
        self.counter = self.maxCounter
        self.checked = {}
        self.checking = {}
#       print('peep heading to {}'.format(self.goal))
        #FIXME: this is broken below
    #   assert self.goal in path_net
        if self.goal not in path_net:
            print('goal not in path net:', self.goal)
            return -1
        # if the peep is off the path...
        if src not in path_net:
            return [src]
        curr_node = path_net[src]
        link_scores = []
        self.checking[curr_node.position] = True
        for adj in curr_node.links:
            if adj in park.path_net:
                adj = park.path_net[adj]
                adj_score = self.dfs_node(park, adj)
                link_scores.append(adj_score)
        adj_paths = sorted(link_scores, key=lambda x:x[1])
        if not adj_paths:
            return [src]
        next_path = adj_paths[0][0].position
        self.checked[curr_node] = adj_paths[0][1]
        self.backtrace_hist = {}
        route = self.backtrace_node(park, [next_path])
       #print('peep found route: {}'.format(route))
        return route

    def find_map(self, park, src, trg):
        ''' this searches over an array '''
        self.goal = trg
        path_net = park.path_net
        self.maxTilesChecked = len(path_net)
        self.counter = self.maxCounter
        self.checked = {}
        self.checking = {}
        link_scores = []
        self.checking[src] = True
        map_arr = park.map
        for adj in self.adj:
            next_pos = (src[0] + adj[0], src[1] + adj[1])
            if 0 <= next_pos[0] < map_arr.shape[1] and 0 <= next_pos[1] < map_arr.shape[2]:
                if (map_arr[Map.RIDE][next_pos[0], next_pos[1]] == -1):
                    adj_score = self.dfs_map(park.map, next_pos, trg)
                    link_scores.append(adj_score)
        adj_paths = sorted(link_scores, key=lambda x:x[1])
        if not adj_paths:
            return [src]
        next_path = adj_paths[0][0]
        self.checked[src] = adj_paths[0][1]
        self.backtrace_hist = {}
        route = self.backtrace_map([next_path])
        return route

    def dfs_map(self, map_arr, src, trg):
        if src in self.checked:
            return src, self.checked[src]
        if src in self.checking:
            return src, float('inf')
        self.checking[src] = True
        link_scores = []
        if src == trg:
            self.checking.pop(src)
            self.checked[src] = 0
            return src, 0
        for adj in self.adj:
            next_pos = (src[0] + adj[0], src[1] + adj[1])
            if 0 <= next_pos[0] < map_arr.shape[1] and 0 <= next_pos[1] < map_arr.shape[2]:
                if (map_arr[Map.RIDE][next_pos[0], next_pos[1]] == -1):
                    adj_score = self.dfs_map(map_arr, next_pos, trg)
                    link_scores.append(adj_score)
        self.checking.pop(src)

        route = sorted(link_scores, key=lambda x:x[1])
        non_inf = 0
        for r in route:
            if r[1] < float('inf'):
                non_inf += 1
        if non_inf == 0:
            score = float('inf')
        else:
            score = route[0][1] + 1
        self.checked[src] = score

        self.counter -= 1
        return src, score

    def backtrace_map(self, paths):
        last_pos = paths[-1]
        self.backtrace_hist[last_pos] = True
        if last_pos in self.checked and self.checked[last_pos] == 0:
            return paths
        link_scores = []
        for adj in self.adj:
            adj_pos = (last_pos[0] + adj[0], last_pos[1] + adj[1])
            if adj_pos not in self.backtrace_hist and adj_pos in self.checked:
                score = self.checked[adj_pos]
                if score == 0:
                    paths.append(adj_pos)
                    return paths
                link_scores.append(adj_pos)
        if not link_scores:
            return paths
        link_scores = sorted(link_scores, key=lambda x:x[1])
        paths.append(link_scores[0])
        return self.backtrace_map(paths)

    def backtrace_node(self, park, paths):
       #print('backtrace', paths)
        last_pos = paths[-1]
        self.backtrace_hist[last_pos] = True
        if last_pos in self.checked and self.checked[last_pos] == 0:
            return paths
        if last_pos not in self.path_net:
            return paths
        last_path = self.path_net[last_pos]
        link_scores = []
        for adj_pos in last_path.links:
            if adj_pos in park.path_net and adj_pos not in self.backtrace_hist and adj_pos in self.checked:
                score = self.checked[adj_pos]
                if score == 0:
                    paths.append(adj_pos)
                    return paths
                link_scores.append((adj_pos, self.checked[adj_pos]))
        if not link_scores:
            return paths
        link_scores = sorted(link_scores, key=lambda x:x[1])
        paths.append(link_scores[0][0])
        return self.backtrace_node(park, paths)

    def dfs_node(self, park, node):
       #print('dfs', node)
       #search_graph = np.ones((50, 50, 3)) * 255
       #rend_arr = np.array(search_graph, dtype=np.uint8)
       #chkd_arr = np.array(search_graph, dtype=np.uint8)
       #for pos in self.checking:
       #    rend_arr[pos[0], pos[1], 0] = 0
       #cv2.imshow("pathfinder checking", rend_arr)
       #cv2.waitKey(1)
       #for pos in self.checked:
       #    chkd_arr[pos[0], pos[1], 1] = int(max(0, 255 - self.checked[pos] * 10))
       #cv2.imshow("pathfinder checked", chkd_arr)
       #cv2.waitKey(1)
        pos = node.position
        if pos in self.checked:
           #rend_arr[pos[0], pos[1], 1] = 0
#           print('FOUND TRACE at {}, distance {}'.format(pos, self.checked[node.position]))
           #cv2.imshow("pathfinder checking", rend_arr)
           #cv2.waitKey(1)
            return node, self.checked[pos]
        if pos in self.checking:
           #self.checked[node.position] = float('inf')
            return node, float('inf')
        self.checking[node.position] = True
        link_scores = []
       #print(node.position, self.goal)
        if node.position == self.goal:
            self.checking.pop(node.position)
#           print('FOUND GOAL')
            pos = node.position
           #rend_arr[pos[0], pos[1], 2] = 0
           #cv2.imshow("pathfinder checking", rend_arr)
           #cv2.waitKey(1)
            self.checked[node.position] = 0
            return node, 0
#       print('node', node)
        for adj in node.links:
            if adj in park.path_net:
                adj = park.path_net[adj]
                link_scores.append(self.dfs_node(park, adj))
        self.checking.pop(node.position)

        route = sorted(link_scores, key=lambda x:x[1])
        non_inf = 0
        for r in route:
            if r[1] < float('inf'):
                non_inf += 1
        #FIXME: Make this work!
       #if self.counter <= 0 or len(self.checked) >= self.maxTilesChecked:
       #    score = self.heuristic_from_goal(node.position)
       #   #self.checked[node.position] = score
        if non_inf == 0:
#           score = self.heuristic_from_goal(pos)
            score = float('inf')
        else:
            score = route[0][1] + 1
        self.checked[node.position] = score

        self.counter -= 1
        return node, score

    def heuristic_from_goal(self, pos:tuple):
        goal = self.goal
        return abs(pos[0]-goal[0])+abs(pos[1]-goal[1])

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
