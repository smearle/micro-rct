import random, time, datetime
from collections import *
from .attraction import Ride_and_Store as RS
from .peep import Peep
from .rct_test_objects import object_list as ride_list
from .rct_test_objects import symbol_list, symbol_dict
from .peeps_generator import generate
import numpy as np
from .tilemap import Map
from .path import Path

from .park import Park


def placePath(park, margin):
    freeSpace = park.freeSpace
    interactiveSpace = park.interactiveSpace
    fixedSpace = park.fixedSpace

    if margin >= park.size[0] or margin >= park.size[1]:
        return

    for i in range(margin+1):
        for j in range(1,margin+1):
            if i==0 and j==1:
                fixedSpace.pop((i,j))
                interactiveSpace[(i,j)] = Park.pathMark
                park.map[Map.PATH, i, j] = 1
            elif j == 1 or (i==margin and j!=margin):
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = Park.pathMark
                park.map[Map.PATH, i, j] = 1

    for i in range(margin, park.size[1] - margin):
        for j in range(margin, park.size[0] - margin):
            if i == margin or i == park.size[1] - margin-1 or j == margin or j == park.size[0] - margin - 1:
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = Park.pathMark
                park.map[Map.PATH, i, j] = 1

    return

def place_path_tile(park, x, y, type_i=0):
#   print('place path tile: ', x, y, type_i)
    pos = (x, y)
    if pos in park.fixedSpace:
        park.fixedSpace.pop(pos)
    if pos in park.freeSpace:
        park.freeSpace.pop(pos)
    park.interactiveSpace[(x, y)] = Park.pathMark
    if pos not in park.path_net:
        park.map[Map.PATH, x, y] = Path.PATH
        path = Path((x, y), park.map[Map.PATH], park.path_net)
        park.path_net[(x, y)] = path
        path.get_connecting()
        for adj_path in path.links:
            if adj_path:
                adj_path.get_connecting()
#   print('path placed')

def place_ride_tile(park, i):
    pass
#   placeRide(park, i)


def placeRide(park, ride_i):
    # print('try to place {}'.format(_ride.name))
    _ride = ride_list[ride_i]() 
    mark = str(symbol_list[ride_i])

    def checkCanPlaceOrNot(startX,startY,width,length):
        # print("check ({},{}) to ({},{})".format(startX,startY,startX+width-1,startY+length-1))

        for i in range(startX,startX+width):
            for j in range(startY,startY+length):
                if (i,j) in park.fixedSpace or (i,j) in park.interactiveSpace:
                    return False

        return True

    size = _ride.size
    placed = False
    potentialPlace = park.freeSpaceNextToInteractiveSpace()
    seen = set()

    while not placed and len(seen) != len(potentialPlace):
        placed = False
        potentialPlaces = list(potentialPlace.keys())

        if len(potentialPlaces) == 0:
            break
        rand = random.choice(potentialPlaces)

        while rand in seen:
            rand = random.choice(list(potentialPlace.keys()))
        seen.add(rand)
        potentialPlace.pop(rand)
        enter = rand
        startList = [(rand[0],rand[1]),(rand[0]-size[0]+1,rand[1]-size[1]+1),(rand[0]-size[0]+1,rand[1]),(rand[0],rand[1]-size[1]+1)]
        startList = [(x,y)for x,y in startList if x>0 and y>0]

        while startList and not placed:
            rand = startList.pop()
            placed = checkCanPlaceOrNot(rand[0],rand[1],size[0],size[1])

        if placed:
            _ride.enter = enter
            _ride.position = rand
            park.listOfRides.append((mark,_ride))
            park.updateMap(rand,size,mark,_ride.enter)
            print('ride {} is placed at {}'.format(_ride.name,_ride.position))
