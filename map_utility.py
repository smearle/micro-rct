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
peepsList = set()
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
    res = '\nprint count: '+str(printCount)+'\n'
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

def updatedMap(start,size,mark:str,entrence=None):
    for i in range(start[0],start[0]+size[1]):
        for j in range(start[1],start[1]+size[0]):
            if (i,j) in freeSpace:
                freeSpace.pop((i,j))
                if mark == pathMark:
                    interactiveSpace[(i,j)] = mark
                else:
                    if entrence and i == entrence[0] and j == entrence[1]: #ride entrence
                        interactiveSpace[(i,j)] = pathMark
                    elif not entrence and i==start[0] and j==start[1]: #ride entrence
                        interactiveSpace[(i,j)] = pathMark
                    else:
                        fixedSpace[(i,j)] = mark
            elif (i,j) in interactiveSpace:
                interactiveSpace[(i,j)] = mark
    return

def updateRides():
    for _,ride in listOfRides:
        if ride.queue:
            curPeep = ride.queue.pop(0)
            curPeep.interactWithRide(ride)
    return

                

def updatedHuman(peep:Peeps):
    if peep not in peepsList:
        peepsList.add(peep)
    else:
        updatedMap(peep.position,(1,1),pathMark)
        peep.updatePosition(interactiveSpace,listOfRides)
    updatedMap(peep.position,(1,1),humanMark)


def placeRide(_ride: RS,mark:str):
    # print('try to place {}'.format(_ride.name))
    def checkCanPlaceOrNot(startX,startY,width,length):
        # print("check ({},{}) to ({},{})".format(startX,startY,startX+width-1,startY+length-1))
        for i in range(startX,startX+width):
            for j in range(startY,startY+length):
                if (i,j) in fixedSpace or (i,j) in interactiveSpace:
                    return False
        return True

    size = _ride.size
    placed = False
    potentialPlace = freeSpaceNextToInteractiveSpace()
    seen = set()
    while not placed and len(seen) != len(potentialPlace):
        placed = False
        rand = random.choice(list(potentialPlace.keys()))
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
            listOfRides.append((mark,_ride))
            updatedMap(rand,size,mark,_ride.enter)
    return

def freeSpaceNextToInteractiveSpace():
    ans = defaultdict(str)
    neighbors = [(1,0),(0,1),(-1,0),(0,-1)]
    for x,y in interactiveSpace:
        for _x,_y in neighbors:
            neighbor = (_x+x,_y+y)
            if neighbor in freeSpace:
                ans[neighbor] = freeSpace[neighbor]
    return ans

