import random
from collections import *
from class_ride_and_store import Ride_and_Store as RS
from class_peeps import Peeps 
from rct_test_objects import object_list as ride
from rct_test_peeps import peeps

parkSize = (45,15)
freeSpace = defaultdict(str)
usedSpace = defaultdict(str)
listOfRides = []
def initPark():
    for i in range(parkSize[1]):
        for j in range(parkSize[0]):
            if i == 0 or j == 0 or j == parkSize[0]-1 or i == parkSize[1]-1:
                usedSpace[(i,j)] = '#'
            freeSpace[(i,j)] = ' '
    updatedMap((0,1),(2,1),'_')

def printPark():
    res = ''
    for i in range(parkSize[1]):
        line = ''
        for j in range(parkSize[0]):
            if (i,j) in usedSpace:
                line += usedSpace[(i,j)]
            else:
                line += freeSpace[(i,j)]
        line += '\n'
        res += line
    print(res)

def updatedMap(start,size,mark:str):
    for i in range(start[0],start[0]+size[1]):
        for j in range(start[1],start[1]+size[0]):
            if (i,j) in freeSpace:
                freeSpace.pop((i,j))
            usedSpace[(i,j)] = mark


def placeRide(_ride: RS,mark:str):
    size = _ride.size
    placed = False
    while not placed:
        placed = True
        rand = random.choice(list(freeSpace.keys()))
        for i in range(rand[0]-1,rand[0]+size[1]):
            for j in range(rand[1]-1,rand[1]+size[0]):
                if (i,j) in usedSpace:
                    placed = False
        if placed:
            _ride.position = rand
            listOfRides.append(_ride)
            updatedMap(rand,size,mark)
    return


def main():
    initPark()
    placeRide(ride[0],'&')
    placeRide(ride[1],'+')
    placeRide(ride[6],'A')
    guest = peeps[0]
    updatedMap(guest.position,(1,1),'O')
    guest.findClosesetRide(listOfRides)
    print('guest: {} heading to {}'.format(guest.id,guest.headingTo))
    printPark()
    return 

main()

