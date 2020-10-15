import datetime 
import random
import time
from collections import *

import numpy as np

from .rct_test_objects import symbol_dict, symbol_list
from .park_enums import PARK
from .path import Path
from .peep import Peep
from .peeps_generator import generate
from .rct_test_objects import object_list as ride_list
from .tilemap import Map
from .utils.debug_utils import print_msg

def placePath(park, margin, verbose=False):
   #freeSpace = park.freeSpace
   #interactiveSpace = park.interactiveSpace
   #fixedSpace = park.fixedSpace

    if margin >= park.size[0] or margin >= park.size[1]:
        return

    for i in range(margin+1):
        for j in range(1,margin+1):
            if i==0 and j==1:
#               fixedSpace.pop((i,j))
#               interactiveSpace[(i,j)] = PARK.pathMark
                park.map[Map.PATH, i, j] = 1
            elif j == 1 or (i==margin and j!=margin):
#               freeSpace.pop((i,j))
#               interactiveSpace[(i,j)] = PARK.pathMark
                park.map[Map.PATH, i, j] = 1

    for i in range(margin, park.size[1] - margin):
        for j in range(margin, park.size[0] - margin):
            if i == margin or i == park.size[1] - margin-1 or j == margin or j == park.size[0] - margin - 1:
#               freeSpace.pop((i,j))
#               interactiveSpace[(i,j)] = PARK.pathMark
                park.map[Map.PATH, i, j] = 1

    return


def place_path_tile(park, x, y, type_i=0, verbose=False, is_entrance=False):
#   print('place path at {}, {}'.format(x, y))
#   print_msg('place path tile: {} {} {}'.format(x, y, type_i), priority=4, verbose=verbose)
    pos = (x, y)

    # will overwrite rides, but not their entrances
    if park.map[Map.RIDE, x, y] != -1 and park.map[Map.PATH, x, y] == -1:
        demolish_tile(park, x, y)
    #   if (x, y) in park.rides_by_pos:
    #       ride = park.rides_by_pos[(x, y)]
    #       for ride_pos in park.pos_by_rides[ride]:
    #           i, j = ride_pos
    #           demolish_tile(park, i, j)
   #if pos in park.fixedSpace:
   #    park.fixedSpace.pop(pos)

   #if pos in park.freeSpace:
   #    park.freeSpace.pop(pos)
   #park.interactiveSpace[(x, y)] = PARK.pathMark
    update_path_net(park, pos, is_entrance=is_entrance)

def update_path_net(park, pos, is_entrance=False):
    if pos not in park.path_net:
        x, y = pos
        park.map[Map.PATH, x, y] = Path.PATH
        path = Path((x, y), park.map[Map.PATH], park.path_net, is_entrance=is_entrance)
        park.path_net[(x, y)] = path
        path.get_connecting(park.path_net)

        for adj_path in path.links:
            if adj_path in park.path_net:
                adj_path = park.path_net[adj_path]
                adj_path.get_connecting(park.path_net)
#   print('path placed')

def demolish_tile(park, x, y):
    if park.map[Map.PEEP, x, y] != -1:
        return False
   #print('demolishing tile {} {}'.format(x, y))
    pos = (x, y)

    if pos in park.path_net:
        path = park.path_net.pop(pos)

        for adj_path in path.links:
            if adj_path in park.path_net:
                adj_path = park.path_net[adj_path]
                adj_path.get_connecting(park.path_net)

#   if pos in park.interactiveSpace:
#       park.interactiveSpace.pop(pos)

    #FIXME: NO!!
    if park.map[Map.RIDE, pos[0], pos[1]] > -1 and not pos in park.locs_to_rides:
        raise Exception('position {}, \n{}\n{}'.format(pos, park.map[Map.RIDE], park.locs_to_rides))
#       park.map[Map.RIDE, pos[0], pos[1]] = -1
    if pos in park.locs_to_rides:
        center = park.locs_to_rides[pos]
        ride = park.rides_by_pos.pop(center)
        assert center == ride.position
        for ride_pos in ride.locs:
            if ride_pos in park.locs_to_rides:
                park.locs_to_rides.pop(ride_pos)
            park.map[Map.RIDE, ride_pos[0], ride_pos[1]] = -1
            demolish_tile(park, ride_pos[0], ride_pos[1])
        

    #   for i in range(x, x + ride.size[0]):
    #       for j in range(y, y + ride.size[1]):
    #           if not (0 <= i < park.map.shape[0] and 0 <= j < park.map.shape[1]):
    #               pass
    #           else:
    #               demolish_tile(park, x, y)

#   park.freeSpace[pos] = PARK.emptyMark
    park.map[Map.PATH, x, y] = -1
    park.map[Map.RIDE, x, y] = -1


def clear_for_placement(park, x, y, dx, dy):
    ''' delete everything in a patch'''
    for i in range(x, x + dx):
        for j in range(y, y + dy):
            demolish_tile(park, i, j)


def place_ride_tile(park, x, y, ride_i, rotation=0):
#   print('placing ride', x, y, ride_i)
    _ride = ride_list[ride_i]()
    mark = str(symbol_list[ride_i])
    size = _ride.size
    if rotation == 0:
        entrance = (x, y)
    elif rotation == 1:
        entrance = (x + size[0] - 1, y)
    elif rotation == 2:
        entrance = (x, y + size[1] - 1)
    elif rotation == 3:
        entrance = (x + size[0] - 1, y + size[1] - 1)
    else:
        raise Exception('invalid entrance position index')

    if checkCanPlaceOrNot(park, _ride, x, y, size[0], size[1]):
        clear_for_placement(park, x, y, size[0], size[1])
        place_path_tile(park, *entrance, is_entrance=True)
        _ride.entrance = entrance
        _ride.position = (x, y)
        _ride.rotation = rotation
        park.rides_by_pos[(x, y)] = _ride
        for i in range(x, x + size[0]):
            for j in range(y, y + size[1]):
                if (not 0 <= i <= park.map.shape[1]) or (not 0 <= j <= park.map.shape[2]):
                   #continue
                   raise Exception('trying to place ride out of map boundaries')
                if (i, j) == entrance:
                    pass
               #else:
               #    demolish_tile(park, i, j)
                park.map[Map.RIDE, i, j] = ride_i
                park.locs_to_rides[(i, j)] = (x, y)
                _ride.locs.append((i, j))
       #park.updateMap((x, y), size, mark, _ride.entrance)
        update_path_net(park, entrance)

    return _ride

def placeRide(park, ride_i, verbose=False):
    # print('try to place {}'.format(_ride.name))
    _ride = ride_list[ride_i]()
    mark = str(symbol_list[ride_i])

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
        entrance = rand
        startList = [(rand[0],rand[1]),(rand[0]-size[0]+1,rand[1]-size[1]+1),(rand[0]-size[0]+1,rand[1]),(rand[0],rand[1]-size[1]+1)]
        startList = [(x,y)for x,y in startList if x>0 and y>0]

        while startList and not placed:
            rand = startList.pop()
            placed = checkCanPlaceOrNot(park, _ride, rand[0], rand[1], size[0], size[1])

        if placed:
            _ride.entrance = entrance
            update_path_net(park, entrance)
            print_msg('ride {} is placed at {}'.format(_ride.name,_ride.position), priority=3, verbose=verbose)

def checkCanPlaceOrNot(park, ride, startX, startY, width, length):
    # print("check ({},{}) to ({},{})".format(startX,startY,startX+width-1,startY+length-1))

    for i in range(startX, startX+width):
        for j in range(startY, startY+length):
            if not (0 <= i < park.map.shape[1] and 0 <=  j < park.map.shape[2]):
                return False

            if not ride.entrance == (i, j) and park.map[Map.PATH, i, j] != -1: # can only have path at entrance
                pass
               #return False

            if park.map[Map.PEEP, i, j] != -1:  # cannot have peeps
                return False

            if park.map[Map.RIDE, i, j] != -1:  # can overwrite rides
                pass


    return True
