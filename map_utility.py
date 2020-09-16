import random, time, datetime
from collections import *
from attraction import Ride_and_Store as RS
from peep import Peeps
from rct_test_objects import object_list as ride
from rct_test_objects import symbol_list, symbol_dict
from peeps_generator import generate
import numpy as np

from park import Park


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
                park.map[1, i, j] = 1
            elif j == 1 or (i==margin and j!=margin):
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = Park.pathMark
                park.map[1, i, j] = 1

    for i in range(margin, park.size[1] - margin):
        for j in range(margin, park.size[0] - margin):
            if i == margin or i == park.size[1] - margin-1 or j == margin or j == park.size[0] - margin - 1:
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = Park.pathMark
                park.map[1, i, j] = 1

    print(park.map[1])

    return




def placeRide(park, _ride: RS,mark:str):
    # print('try to place {}'.format(_ride.name))
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
