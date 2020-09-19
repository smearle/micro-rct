from collections import defaultdict
import numpy as np
import cv2
class PathFinder:
    def __init__(self, path_net):
        self.maxCounter = self.counter = 100
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
     #  cv2.namedWindow("pathfinder checking", cv2.WINDOW_NORMAL)
     #  cv2.namedWindow("pathfinder checked", cv2.WINDOW_NORMAL)


    def find(self, peep):
        path_net = self.path_net
        self.checked = {}
        self.checking = {}
        self.goal = peep.headingTo.enter
        assert self.goal in path_net
        curr_node = path_net[peep.position]
        link_scores = []
        self.checking[curr_node.position] = True
        for adj in curr_node.links:
            if adj:
                adj_score = self.dfs(adj)
                link_scores.append(adj_score)
        adj_paths = sorted(link_scores, key=lambda x:x[1])
        next_path = adj_paths[0][0].position
        self.checked[curr_node] = adj_paths[0][1]
        route = self.backtrace([next_path])
        return route

    def backtrace(self, paths):
        last_pos = paths[-1]
        if last_pos in self.checked and self.checked[last_pos] == 0:
            return paths
        last_path = self.path_net[last_pos]
        link_scores = []
        for adj in last_path.links:
            if adj and adj.position in self.checked:
                adj_pos = adj.position
                score = self.checked[adj_pos]
                if score == 0:
                    paths.append(adj_pos)
                    return paths
                link_scores.append((adj_pos, self.checked[adj_pos]))
        if not link_scores:
            return paths
        link_scores = sorted(link_scores, key=lambda x:x[1])
        paths.append(link_scores[0][0])
        return self.backtrace(paths)

    def dfs(self, node):
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
      #     rend_arr[pos[0], pos[1], 1] = 0
           #print('FOUND TRACE at {}, distance {}'.format(pos, self.checked[node.position]))
      #     cv2.imshow("pathfinder checking", rend_arr)
      #     cv2.waitKey(1)
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
      #     rend_arr[pos[0], pos[1], 2] = 0
      #     cv2.imshow("pathfinder checking", rend_arr)
      #     cv2.waitKey(1)
            self.checked[node.position] = 0
            return node, 0
        for adj in node.links:
            if adj:
                link_scores.append(self.dfs(adj))
        self.checking.pop(node.position)

        route = sorted(link_scores, key=lambda x:x[1])
        non_inf = 0
        for r in route:
            if r[1] < float('inf'):
                non_inf += 1
        if non_inf == 0:
            score = float('inf')
        else:
            score = route[0][1] + 1
            self.checked[node.position] = score
        return node, score

class Path:
    GRASS = 0
    PATH = 1
    VOMIT = 2

    def __repr__(self):
        return 'Path at {}'.format(self.position)

    def __init__(self, position, path_map, path_net):
        self.name = 'path'
        self.path_net = path_net
        self.position = position
        self.enter = position
        self.path_map = path_map

    def get_connecting(self):
        self.west = self.get_adjacent((-1, 0))
        self.north = self.get_adjacent((0, 1))
        self.east = self.get_adjacent((1, 0))
        self.south = self.get_adjacent((0, -1))
        self.links = [self.west, self.north, self.east, self.south]
        connections = 0
        for l in self.links:
            if l:
                connections += 1
        if connections > 2:
            self.junction = True
        else:
            self.junction = False

    def get_adjacent(self, direction):
        adj_pos = (self.position[0] + direction[0],
                   self.position[1] + direction[1],
                   )
        if adj_pos in self.path_net:
            return self.path_net[adj_pos]
        elif self.path_map[adj_pos] >0:
            return Path(adj_pos, self.path_map, self.path_net)
        return None
