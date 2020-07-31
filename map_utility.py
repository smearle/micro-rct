import random
from collections import *
from class_ride_and_store import Ride_and_Store as RS
from class_peeps import Peeps 
from rct_test_objects import object_list as ride
from rct_test_peeps import peeps

printCount = 1
parkSize = (0,0)
freeSpace = defaultdict(str)
fixedSpace = defaultdict(str)
interactiveSpace = defaultdict(str)
humanMark = 'Ü'
emptyMark = ' '
pathMark = '░'
wallMark = '▓'
listOfRides = []

def initPark(parkSizeX,parkSizeY):
    global parkSize
    parkSize = (parkSizeX,parkSizeY)
    for i in range(parkSize[1]):
        for j in range(parkSize[0]):
            if i == 0 or j == 0 or j == parkSize[0]-1 or i == parkSize[1]-1:
                fixedSpace[(i,j)] = wallMark
            else:
                freeSpace[(i,j)] = emptyMark

def placePath(margin):
    global parkSize
    if margin >= parkSize[0] or margin >= parkSize[1]:
        return
    for i in range(margin+1):
        for j in range(1,margin+1):
            if i==0 and j==1:
                fixedSpace.pop((i,j))
                interactiveSpace[(i,j)] = pathMark
            elif j == 1 or (i==margin and j!=margin):
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = pathMark

    for i in range(margin,parkSize[1]-margin):
        for j in range(margin,parkSize[0]-margin):
            if i == margin or i == parkSize[1]-margin-1 or j == margin or j == parkSize[0]-margin-1:
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = pathMark
    return

def printPark():
    global printCount
    res = 'print count: '+str(printCount)+'\n'
    for i in range(parkSize[1]):
        line = ''
        for j in range(parkSize[0]):
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
    res += 'human: '+humanMark+"\n"
    res += 'enter: '+pathMark+'\n'
    print(res)
    printCount += 1

def updatedMap(start,size,mark:str):
    for i in range(start[0],start[0]+size[1]):
        for j in range(start[1],start[1]+size[0]):
            if mark == emptyMark:
                if (i,j) in interactiveSpace:
                    interactiveSpace.pop((i,j))
                    freeSpace[(i,j)] = emptyMark
            else:
                if (i,j) in freeSpace:
                    freeSpace.pop((i,j))
                if mark == pathMark or mark == humanMark:
                    interactiveSpace[(i,j)] = mark
                else:
                    if i==start[0] and j==start[1]:
                        fixedSpace[(i,j)] = pathMark
                    else:
                        fixedSpace[(i,j)] = mark

def updatedHuman(peep:Peeps):
    updatedMap(peep.position,(1,1),emptyMark)
    peep.updatePosition(freeSpace)
    if peep.headingTo:
        updatedMap(peep.position,(1,1),humanMark)


def placeRide(_ride: RS,mark:str,padding=None):
    size = _ride.size
    placed = False
    if not padding:
        padding = 0
    while not placed:
        placed = True
        rand = random.choice(list(freeSpace.keys()))
        for i in range(rand[0]-padding,rand[0]+size[1]+padding):
            for j in range(rand[1]-padding,rand[1]+size[0]+padding):
                if (i,j) in fixedSpace:
                    placed = False
        if placed:
            _ride.position = rand
            listOfRides.append((mark,_ride))
            updatedMap(rand,size,mark)
    return


