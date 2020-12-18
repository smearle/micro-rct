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
               #fixedSpace.pop((i,j))
               #interactiveSpace[(i,j)] = PARK.pathMark
#               park.map[Map.PATH, i, j] = 1
                place_path_tile(park, i, j)
                park.fixedSpace.add((i, j))
            elif j == 1 or (i==margin and j!=margin):
               #freeSpace.pop((i,j))
               #interactiveSpace[(i,j)] = PARK.pathMark
#               park.map[Map.PATH, i, j] = 1
                place_path_tile(park, i, j)
                park.fixedSpace.add((i, j))

    for i in range(margin, park.size[1] - margin):
        for j in range(margin, park.size[0] - margin):
            if i == margin or i == park.size[1] - margin-1 or j == margin or j == park.size[0] - margin - 1:
               #freeSpace.pop((i,j))
               #interactiveSpace[(i,j)] = PARK.pathMark
#               park.map[Map.PATH, i, j] = 1
                place_path_tile(park, i, j)
                park.fixedSpace.add((i, j))

    return

def try_place_path_tile(park, x, y, type_i=0, verbose=False, is_entrance=False):
    if checkCanPlaceOrNot(park, x, y, 1, 1):
        place_path_tile(park, x, y, type_i=type_i, verbose=verbose, is_entrance=is_entrance)

def place_path_tile(park, x, y, type_i=0, verbose=False, is_entrance=False):
#   print('place path at {}, {}'.format(x, y))
#   print_msg('place path tile: {} {} {}'.format(x, y, type_i), priority=4, verbose=verbose)
    pos = (x, y)

    if park.map[Map.PATH, x, y] != -1:
        return True

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
            if adj_path:
                adj_path.get_connecting(park.path_net)
#   print('path placed')

def try_demolish_tile(park, x, y):
    pos = (x, y)
    res = False
    if park.map[Map.RIDE, pos[0], pos[1]] > -1 and not pos in park.locs_to_rides:
        raise Exception('position {}, \n{}\n{}'.format(pos, park.map[Map.RIDE], park.locs_to_rides))
#       park.map[Map.RIDE, pos[0], pos[1]] = -1
    if pos in park.locs_to_rides:
        center = park.locs_to_rides[pos]
        if center not in park.rides_by_pos:
            raise Exception

        # if we're about to demolish a ride tile, make sure we are good to demolish the entire ride
        ride = park.rides_by_pos[center]
        if not checkCanPlaceOrNot(park, center[0], center[1], ride.size[0], ride.size[1]):
            return False
        else:
            return demolish_tile(park, center[0], center[1])
    
    if checkCanPlaceOrNot(park, x, y, 1, 1):
        res = demolish_tile(park, x, y)
        assert res
    return res

    #   for i in range(x, x + ride.size[0]):
    #       for j in range(y, y + ride.size[1]):
    #           if not (0 <= i < park.map.shape[0] and 0 <= j < park.map.shape[1]):
    #               pass

def demolish_tile(park, x, y):
    if park.map[Map.PEEP, x, y] != -1:
        raise Exception
#   print('demolishing tile {} {}'.format(x, y))
    pos = (x, y)

    if pos in park.path_net:
        path = park.path_net.pop(pos)
        path.get_connecting(park.path_net)

        for adj_path in path.links:
            if adj_path:
                adj_path.get_connecting(park.path_net)

#   if pos in park.interactiveSpace:
#       park.interactiveSpace.pop(pos)

    #FIXME: NO!!

    if park.map[Map.RIDE, pos[0], pos[1]] > -1 and not pos in park.locs_to_rides:
        raise Exception('position {}, \n{}\n{}'.format(pos, park.map[Map.RIDE], park.locs_to_rides))
#       park.map[Map.RIDE, pos[0], pos[1]] = -1
    if pos in park.locs_to_rides:
        center = park.locs_to_rides[pos]
        if center not in park.rides_by_pos:
            raise Exception

        ride = park.rides_by_pos[center]
        if not checkCanPlaceOrNot(park, center[0], center[1], ride.size[0], ride.size[1]):
            raise Exception('demolishing tile but ride is not removable')
            return False
        # important to do this here, lest we recursively demolish entire ride patch repeatedly
        ride = park.rides_by_pos.pop(center)
        # Deleting a ride gives the park a full refund on the ride's original cost
        park.money += ride.build_cost
        assert center == ride.position

        for ride_pos in ride.locs:
            if ride_pos in park.locs_to_rides:
                park.locs_to_rides.pop(ride_pos)
            park.map[Map.RIDE, ride_pos[0], ride_pos[1]] = -1
            park.map[Map.PATH, ride_pos[0], ride_pos[1]] = -1
            assert park.map[Map.PEEP, ride_pos[0], ride_pos[1]] == -1
            # this is strictly to get rid of the path object
            res = demolish_tile(park, ride_pos[0], ride_pos[1])

           #if not res:
           #    raise Exception
           #    return res
    #   for i in range(x, x + ride.size[0]):
    #       for j in range(y, y + ride.size[1]):
    #           if not (0 <= i < park.map.shape[0] and 0 <= j < park.map.shape[1]):
    #               pass
    #           else:
    #               demolish_tile(park, x, y)

#   park.freeSpace[pos] = PARK.emptyMark
    park.map[Map.PATH, x, y] = -1
    park.map[Map.RIDE, x, y] = -1

    return True


def clear_for_placement(park, x, y, dx, dy):
    ''' delete everything in a patch. We must already know that this is a valid thing to do.'''
    result = True

    for i in range(x, x + dx):
        for j in range(y, y + dy):
            res_ij = demolish_tile(park, i, j)

            if not res_ij:
                print(park.printPark())
                print(x, y, dx, dy)
                print(park.map[Map.PEEP, i, j])
                raise Exception

                return res_ij

    return result

def _add_ride(park, _ride, x, y, ride_i, entrance):
    '''
    Adding ride to relevant data structures, once placement is confirmed.
    '''
    size = _ride.size
    place_path_tile(park, *entrance, is_entrance=True)
    _ride.entrance = entrance
    _ride.position = (x, y)
#   _ride.rotation = rotation
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
    assert _ride.entrance in park.path_net
    park.money -= _ride.build_cost
    assert park.money >= 0
    return _ride

def place_ride_tile(park, x, y, ride_i, rotation=0, destructive=True):
    '''
    destructive: are we allowed to delete path and other rides?
    '''
#   print('placing ride', x, y, ride_i)
    _ride = ride_list[ride_i]()
    size = _ride.size

    if ride_i < 0:
        ride_i = len(ride_list) + ride_i
    mark = str(symbol_list[ride_i])

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

    build_budget = park.money - _ride.build_cost
    if checkCanPlaceOrNot(park, x, y, size[0], size[1], destructive=destructive, budget=build_budget):
        result = clear_for_placement(park, x, y, size[0], size[1])
#       print('clear_for_placement result:', result)

        if not result:
            raise Exception

            return result
        _ride = _add_ride(park, _ride, x, y, ride_i, entrance)

       #print('placed ride type {} at ({}, {})'.format(ride_i, x, y))
        return _ride
    else:
       #print('failed to place ride type {} at ({}, {})'.format(ride_i, x, y))
        return False

def placeRide(park, ride_i, verbose=False):
    _ride = ride_list[ride_i]()
   #print('try to place {}'.format(_ride.name))
    mark = str(symbol_list[ride_i])

    size = _ride.size
    placed = False
    potentialPlace = park.freeSpaceNextToInteractiveSpace()
    seen = set()

    while len(seen) < len(potentialPlace):
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
            build_budget = park.money - _ride.build_cost
            placed = checkCanPlaceOrNot(park,rand[0],rand[1],size[0],size[1], destructive=True, budget=build_budget)

        if placed:
            result = clear_for_placement(park, rand[0], rand[1], size[0], size[1])
            assert result
            _ride.entrance = entrance
            _ride.position = rand
            _add_ride(park, _ride, rand[0], rand[1], ride_i, entrance)
           #park.updateMap(rand,size,mark,_ride.entrance)
            
            print_msg('ride {} is placed at {}'.format(_ride.name,_ride.position), priority=3, verbose=verbose)
            return

# TODO: just give this guy the ride object. Would be less sketchy.
def checkCanPlaceOrNot(park, startX, startY, width, length, destructive=True, budget=None):
    '''
    destructive: are we allowed to delete paths and rides?
    - the cost of the ride to be placed must be subtracted in advance from the budget. So we may enter this function with a negative budget. This will return True iff the budget - cost is positive. For now the cost is positive (deleting rides always gets you some kind of refund).
    '''
    # print("check ({},{}) to ({},{})".format(startX,startY,startX+width-1,startY+length-1))

    cost = 0
    checked_rides = set()
    checking = set()
    checked_ride_centers = set()

    for i in range(startX, startX+width):
        for j in range(startY, startY+length):
            if not (0 <= i < park.map.shape[1] and 0 <=  j < park.map.shape[2]):
                # this would be off-map
                return False
            checking.add((i, j))

    while checking:
        (i, j) = checking.pop()

        if not (0 <= i < park.map.shape[1] and 0 <=  j < park.map.shape[2]):
            raise Exception('existing ride location off-map', i, j)
            return False

       #if not ride.entrance == (i, j) and park.map[Map.PATH, i, j] != -1: # can only have path at entrance
       #    pass
       #   #return False

        if park.map[Map.PEEP, i, j] != -1:  # cannot have peeps
            return False

        if not destructive:
            if park.map[Map.RIDE, i, j] != -1 or park.map[Map.PATH, i, j] != -1:
                return False

        if (i, j) in park.fixedSpace:
            # Do not demolish the sacred donut
            return False

        if park.map[Map.RIDE, i, j] != -1:  # can overwrite rides
            ride_ij_pos = park.locs_to_rides[(i, j)]
            # if we're checking if a ride is deletable, avoid infinite recursion
            if ride_ij_pos in checked_rides:
                continue
            if ride_ij_pos not in park.rides_by_pos:
                print(park.printPark())
                print(ride_ij_pos)
                print(park.locs_to_rides)
                print(park.rides_by_pos)
                raise Exception
            ride_ij = park.rides_by_pos[ride_ij_pos]
            if ride_ij_pos not in checked_ride_centers:
                # following through with the placement will refund us all rides deleted in the process
                cost -= ride_ij.build_cost
                checked_ride_centers.add(ride_ij_pos)
            for ride_pos in ride_ij.locs:
               #print(ride_ij.locs)
                checking.add(ride_pos)
            checked_rides.add((i, j))
    if budget is not None:
        if budget - cost >= 0:
            return True
        else:
            return False

    return True
