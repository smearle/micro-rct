import copy
import datetime
import random
import sys
import time
from collections import *

import numpy as np

from .peep import Peep
from .map_utility import *
from .park_enums import PARK
from .path import Path
#from .map import Map
from .tilemap import Map
from .utils.debug_utils import print_msg
from .rct_test_objects import symbol_dict, symbol_list

np.set_printoptions(linewidth=200, threshold=sys.maxsize)

class Park():
    humanMark = 'Ü'
    humanMark2 = '2'
    humanMark3 = '3'
    emptyMark = ' '
    pathMark = '░'
    wallMark = '▓'
    INIT_MONEY = 0
    MARKS_TO_RIDES = {
            emptyMark: 'empty',
            wallMark: 'wall',
            }
    VOMIT_LIFESPAN = 40
    PATH = 0,

    def __init__(self, settings):
        self.startTime = 0
        self.printCount = 1
        self.parkSize = (0,0)
        self.size = (settings['environment']['map_width'],settings['environment']['map_height'])
        self.settings=settings
        self.startTime = time.time()
        # channels for rides, paths, peeps
        self.map = np.zeros((5, self.size[0], self.size[1]), dtype=int) - 1
        self.freeSpace = defaultdict(str)
        self.fixedSpace = defaultdict(str)
#       self.interactiveSpace = defaultdict(str)
        self.rides_by_pos = {}
        self.locs_to_rides = {}

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                # I'm ignoring walls for now. Do we need/want them?
                if False:
                    pass
#               if i == 0 or j == 0 or j == self.size[0] - 1 or i == self.size[1] - 1:
#                   self.fixedSpace[(i,j)] = Park.wallMark
#                   self.map[[0,1], i, j] = -1
                else:
                    self.freeSpace[(i, j)] = Park.emptyMark
                    self.map[0, i, j] = -1

        self.peepsList = set()
#       self.listOfRides = []
        self.avg_peep_happiness = 0
        self.path_net = {}
        self.vomit_paths = {}
        self.money = Park.INIT_MONEY
        self.last_money = self.money
        self.income = 0

    def clone(self, settings):
        new_park = Park(settings)
       #new_park.rides_by_pos = copy.deepcopy(self.rides_by_pos)
        new_park.rides_by_pos = {}
        new_park.locs_to_rides = {}

        for peep in self.peepsList:
            new_park.map[Map.PEEP, peep.position[0],
                    peep.position[1]] = -1

        for pos, ride in self.rides_by_pos.items():
#           print('replicating ride', ride)
            x = ride.position[0]
            y = ride.position[1]
            assert (x, y) == pos
            ride_i = self.map[Map.RIDE, x, y]
#           new_ride = ride_list[ride_i]()
            place_ride_tile(new_park,
                             x,
                             y,
                             ride_i)
           #for loc in ride.locs:
           #    new_park.locs_to_rides[loc] = pos
           #new_park.rides_by_pos[(x, y)] = ride
        for pos in self.path_net:
            place_path_tile(new_park, pos[0], pos[1])


        return new_park

    def add_vomit(self, pos):
        x, y = pos
        self.map[Map.PATH, x, y] = Path.VOMIT
        # non-path immediately absorbs vomit for now

        if (x, y) not in self.path_net:
            return
        path_tile = self.path_net[x, y]
        path_tile.vom_time = PARK.VOMIT_LIFESPAN
        self.vomit_paths[x, y] = path_tile

    def populate_path_net(self):
        '''
        Create graph of Path objects after initial path is placed.
        TODO: A simpler version of this in the case where path changes
        '''
        # locate all paths on the map
        path_coords = np.nonzero(self.map[Map.PATH] > 0)
        path_coords = np.array(path_coords)
        path_coords_T = path_coords.transpose()

        #initialize an object for each

        for position in path_coords_T:
            position = tuple(position)

            if position not in self.path_net:
                self.path_net[position] = Path(position, self.map[Map.PATH], self.path_net)

        for path in self.path_net.values():
            path.get_connecting(self.path_net)
       #print('path map: \n{}.format(self.map[Map.PATH]))


    def freeSpaceNextToInteractiveSpace(self):
        ans = defaultdict(str)
        neighbors = [(1,0), (0,1), (-1,0), (0,-1)]

        for x,y in self.path_net:
            path = self.path_net[(x, y)]
            if path.is_entrance:
                continue
            for _x,_y in neighbors:
                neighbor = (_x+x,_y+y)

                if neighbor in self.freeSpace:
                    ans[neighbor] = self.freeSpace[neighbor]

        return ans


    def updateScore(self):
        ''' Calculates the score of the park as the average guest happiness. '''
       #print('debug ride dict')
       #for k in self.rides_by_pos:
       #    print(self.rides_by_pos[k])
       #    print(self.path_net[k])
        score = 0
        n_score = 0
        
        for peep in self.peepsList:
            score += peep.happiness
            n_score += peep.nausea
        self.avg_peep_happiness = score / len(self.peepsList)
        self.avg_peep_nausea = n_score / len(self.peepsList)

    def returnScore(self,opt=1):
        self.updateScore()
        if opt == 1:
            return self.avg_peep_happiness
        return self.avg_peep_nausea
        


    # TODO: I think this function is mostly redundanat at this point?
#   def updateMap(self, start, size, mark:str, entrance=None):
#       for i in range(start[0], start[0] + size[0]):
#           for j in range(start[1], start[1] + size[1]):
#               if (i, j) in self.freeSpace:
#                   self.freeSpace.pop((i, j))

#                   if mark == PARK.pathMark:
#                       self.interactiveSpace[(i, j)] = mark
#                       self.map[1, i, j] = 1
#                   else:
#                       if (entrance and i == entrance[0] and j == entrance[1]) or (not entrance and i==start[0] and j==start[1]): #ride entrance
#                           if size != (1, 1):
#                               self.interactiveSpace[(i, j)] = PARK.pathMark
#                           else:
#                               self.interactiveSpace[(i,j)] = mark
#                           self.map[1, i, j] = 1
#                       else:
#                           self.fixedSpace[(i,j)] = mark

#                       if mark != PARK.wallMark:
#                           if mark == PARK.humanMark:
#                               self.map[Map.PEEP, i, j] = 1
#                           assert(isinstance(symbol_dict[mark][0], int), 'symbol dict is fucked up {}'.format(symbol_dict))
#                           else:
#                               self.map[0, i, j] = symbol_dict[mark][0]
#               elif (i, j) in self.interactiveSpace:
#                   self.interactiveSpace[(i,j)] = mark


#       return


    def update(self, frame):
        res = []

        for peep in self.peepsList:
            res += self.updateHuman(peep)
        res += self.updateRides()
        self.updateScore()

        if res != []:
           #self.printPark(frame)
            pass

            for line in res:
                print_msg(line, priority=3, verbose=self.settings['general']['verbose'])


        dead_vomit = []

        for pos, path_tile in self.vomit_paths.items():
            path_tile.vom_time -= 1

            if path_tile.vom_time == 0:
                dead_vomit.append(pos)
                x, y = pos
                self.map[Map.PATH, x, y] = Path.PATH

        for pos in dead_vomit:
            self.vomit_paths.pop(pos)

        self.income = self.money - self.last_money
        self.last_money = self.money


    def updateRides(self):
#       listOfRides = self.listOfRides
        res = []

        for ride in self.rides_by_pos.values():

            if ride.name == 'FirstAid': #peep will remove themselves when the criterial meets
                for curPeep in ride.queue:
                    res += curPeep.interactWithRide(ride)
            elif ride.queue:    #otherwise, ride remove peeps
                curPeep = ride.queue.pop(0)
                res += curPeep.interactWithRide(ride)

        return  res


    def updateHuman(self, peep:Peep):
        res = []
        if peep.type == 0:
            _mark = Park.humanMark
       #    channel = 2
        elif peep.type == 1:
            _mark = Park.humanMark2
       #    channel = 3
        else:
            _mark = Park.humanMark3
       #    channel = 4
            
        if peep not in self.peepsList:
            self.peepsList.add(peep)
            print_msg(vars(peep), priority=3, verbose=self.settings['general']['verbose'])
        else:
            self.map[Map.PEEP, peep.position[0], peep.position[1]] = -1
            res += peep.updatePosition(self.path_net, self.rides_by_pos, self.vomit_paths)
            res += peep.updateStatus(self.rides_by_pos)
        
       #self.updateMap(peep.position, (1,1), _mark
        self.map[Map.PEEP, peep.position[0], peep.position[1]] = peep.type

        return res

    # TODO: implement this using numpy game map!
    def printPark(self, frame=0):
        rides_by_pos = self.rides_by_pos
        res = 'print count: {} at {} frame\n'.format(self.printCount, frame)

        res += ''.join([Park.wallMark for _ in range(self.size[0] + 2)]) + '\n'
        for j in range(self.size[1]):
            line = ''
            line += Park.wallMark
            for i in range(self.size[0]):
                repped = False
                if self.map[Map.PEEP, i, j] != -1:
                    line += Park.humanMark
                    repped = True
                ride_i = self.map[Map.RIDE, i, j]
                if not repped and ride_i != -1:
                    line += symbol_list[ride_i]
                    repped = True
                # TODO: represent vomit as ascii character
                if not repped and self.map[Map.PATH, i, j] != -1:
                    line += Park.pathMark
                    repped = True
                if not repped:
                    line += Park.emptyMark
            line += Park.wallMark
            line += '\n'
            res += line
        res += ''.join([Park.wallMark for _ in range(self.size[0] + 2)]) + '\n'
        res += '\n'

        legend = []
        for ride in rides_by_pos.values():
            mark = ride.symbol
            if mark not in legend:
                res += ride.name + ': {}\n'.format(ride.symbol)
                legend.append(mark)
        res += 'human: {}\n'.format(Park.humanMark)
        res += 'enter: {}\n'.format(Park.pathMark)
        res += '\npark score: {}\n'.format(self.avg_peep_happiness)
        print_msg(res, priority=2, verbose=self.settings['general']['verbose'])
        self.printCount += 1
        return res

    def n_unique_rides(self):
        rides = defaultdict(int)
        for ride in self.rides_by_pos.values():
            rides[ride.name]+=1
        return len(rides)