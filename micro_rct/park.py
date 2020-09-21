import copy
import datetime
import random
import sys
import time
from collections import *

import numpy as np

from .peep import Peep
from .map_utility import *
from .path import Path
#from .map import Map
from .tilemap import Map

np.set_printoptions(linewidth=200, threshold=sys.maxsize)

class Park():
    humanMark = 'Ü'
    emptyMark = ' '
    pathMark = '░'
    wallMark = '▓'
    MARKS_TO_RIDES = {
            emptyMark: 'empty',
            wallMark: 'wall',
            }
    VOMIT_LIFESPAN = 40
    def __init__(self, width, height):
        self.startTime = 0
        self.printCount = 1
        self.parkSize = (0,0)
        self.size = (width,height)
        self.startTime = time.time()
        # channels for rides, paths, peeps
        self.map = np.zeros((3, width, height), dtype=int)
        self.freeSpace = defaultdict(str)
        self.fixedSpace = defaultdict(str)

        for i in range(width):
            for j in range(height):
                if i == 0 or j == 0 or j == self.size[0] - 1 or i == self.size[1] - 1:
                    self.fixedSpace[(i,j)] = Park.wallMark
                    self.map[[0,1], i, j] = -1
                else:
                    self.freeSpace[(i,j)] = Park.emptyMark
                    self.map[0, i, j] = -1

        self.interactiveSpace = defaultdict(str)
        self.peepsList = set()
        self.listOfRides = []
        self.score = 0
        self.path_net = {}
        self.vomit_paths = {}

    def add_vomit(self, pos):
        x, y = pos
        self.map[Map.PATH, x, y] = Path.VOMIT
        path_tile = self.path_net[x, y]
        path_tile.vom_time = self.VOMIT_LIFESPAN
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
            path.get_connecting()


    def freeSpaceNextToInteractiveSpace(self):
        ans = defaultdict(str)
        neighbors = [(1,0), (0,1), (-1,0), (0,-1)]

        for x,y in self.interactiveSpace:
            for _x,_y in neighbors:
                neighbor = (_x+x,_y+y)

                if neighbor in self.freeSpace:
                    ans[neighbor] = self.freeSpace[neighbor]

        return ans


    def updateScore(self):
        ''' Calculates the score of the park as the average guest happiness. '''
        score = 0

        for peep in self.peepsList:
            score += peep.happiness
        self.score = score / len(self.peepsList)


    def updateMap(self, start, size, mark:str, entrance=None):
        for i in range(start[0], start[0] + size[1]):
            for j in range(start[1], start[1] + size[0]):
                if (i, j) in self.freeSpace:
                    self.freeSpace.pop((i, j))

                    if mark == Park.pathMark:
                        self.interactiveSpace[(i, j)] = mark
                        self.map[1, i, j] = 1
                    else:
                        if (entrance and i == entrance[0] and j == entrance[1]) or (not entrance and i==start[0] and j==start[1]): #ride entrance
                            if size != (1, 1):
                                self.interactiveSpace[(i, j)] = Park.pathMark
                            else:
                                self.interactiveSpace[(i,j)] = mark
                            self.map[1, i, j] = 1
                        else:
                            self.fixedSpace[(i,j)] = mark

                        if mark != Park.wallMark:
                            assert isinstance(symbol_dict[mark][0], int)
                            self.map[0, i, j] = symbol_dict[mark][0]
                elif (i, j) in self.interactiveSpace:
                    self.interactiveSpace[(i,j)] = mark

                #elf.map[0, i, j] = symbol_dict[mark][0]

        return


    def update(self, frame):
        res = []

        for peep in self.peepsList:
            res += self.updateHuman(peep)
        res += self.updateRides()
        self.updateScore()

        if res != []:
            self.printPark(frame)

            for line in res:
                print(line)

        
        dead_vomit = []
        for pos, path_tile in self.vomit_paths.items():
            path_tile.vom_time -= 1

            if path_tile.vom_time == 0:
                dead_vomit.append(pos)
                x, y = pos
                self.map[Map.PATH, x, y] = Path.PATH
        for pos in dead_vomit:
            self.vomit_paths.pop(pos)


    def updateRides(self):
        listOfRides = self.listOfRides
        res = []

        for _,ride in listOfRides:
            if ride.name == 'FirstAid': #peep will remove themselves when the criterial meets
                for curPeep in ride.queue:
                    res += curPeep.interactWithRide(ride)
            elif ride.queue:    #otherwise, ride remove peeps
                curPeep = ride.queue.pop(0)
                res += curPeep.interactWithRide(ride)

        return  res


    def updateHuman(self, peep:Peep):
        res = []

        if peep not in self.peepsList:
            self.peepsList.add(peep)
            print(vars(peep))
        else:
            self.updateMap(peep.position, (1,1), Park.pathMark)
            self.map[2, peep.position[0], peep.position[1]] = 0
            res += peep.updatePosition(self.interactiveSpace, self.listOfRides)
            res += peep.updateStatus(self.listOfRides)
        self.updateMap(peep.position, (1,1), Park.humanMark)
        self.map[2, peep.position[0], peep.position[1]] = 1

        return res

    def printPark(self, frame=0):
        startTime = self.startTime
        interactiveSpace = self.interactiveSpace
        freeSpace = self.freeSpace
        fixedSpace = self.fixedSpace
        listOfRides = self.listOfRides

        res = 'print count: {} at {} frame\n'.format(self.printCount, frame)

        for i in range(self.size[1]):
            line = ''

            for j in range(self.size[0]):
                if (i,j) in interactiveSpace:
                    line += interactiveSpace[(i,j)]
                elif (i,j) in freeSpace:
                    line += freeSpace[(i,j)]
                else:
                    line += fixedSpace[(i,j)]
            line += '\n'
            res += line
        res+='\n'

        for mark,ride in listOfRides:
            res += ride.name +': '+mark+'\n'
        res += 'human: '+Park.humanMark+"\n"
        res += 'enter: '+Park.pathMark+'\n'
        res += '\npark score: {}\n'.format(self.score)
        print(res)
        self.printCount += 1
