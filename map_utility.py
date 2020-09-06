import random, time, datetime
from collections import *
from class_ride_and_store import Ride_and_Store as RS
from class_peeps import Peeps
from rct_test_objects import object_list as ride
from rct_test_objects import symbol_list
from peeps_generator import generate

humanMark = 'Ü'
emptyMark = ' '
pathMark = '░'
wallMark = '▓'

class Park():
    def __init__(self):
        self.startTime = 0
        self.printCount = 1
        self.parkSize = (0,0)
        self.freeSpace = defaultdict(str)
        self.fixedSpace = defaultdict(str)
        self.interactiveSpace = defaultdict(str)
        self.peepsList = set()
        self.listOfRides = []
        self.score = 0


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

                    if mark == pathMark:
                        interactiveSpace[(i, j)] = mark
                    else:
                        if (entrance and i == entrance[0] and j == entrance[1]) or (not entrance and i==start[0] and j==start[1]): #ride entrance
                            if size != (1, 1):
                                self.interactiveSpace[(i, j)] = pathMark
                            else:
                                self.interactiveSpace[(i,j)] = mark
                        else:
                            self.fixedSpace[(i,j)] = mark
                elif (i,j) in self.interactiveSpace:
                    self.interactiveSpace[(i,j)] = mark

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


    def updateHuman(self, peep:Peeps):
        res = []

        if peep not in self.peepsList:
            self.peepsList.add(peep)
            print(vars(peep))
        else:
            self.updateMap(peep.position, (1,1), pathMark)
            res += peep.updatePosition(self.interactiveSpace, self.listOfRides)
            res += peep.updateStatus(self.listOfRides)
        self.updateMap(peep.position, (1,1), humanMark)

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
        res += 'human: '+humanMark+"\n"
        res += 'enter: '+pathMark+'\n'
        res += '\npark score: {}\n'.format(self.score)
        print(res)
        self.printCount += 1



def initPark(parkSizeX,parkSizeY):
    park = Park()
    park.size = (parkSizeX,parkSizeY)
    park.startTime = time.time()

    for i in range(park.size[1]):
        for j in range(park.size[0]):
            if i == 0 or j == 0 or j == park.size[0] - 1 or i == park.size[1] - 1:
                park.fixedSpace[(i,j)] = wallMark
            else:
                park.freeSpace[(i,j)] = emptyMark

    return park

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
                interactiveSpace[(i,j)] = pathMark
            elif j == 1 or (i==margin and j!=margin):
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = pathMark

    for i in range(margin, park.size[1] - margin):
        for j in range(margin, park.size[0] - margin):
            if i == margin or i == park.size[1] - margin-1 or j == margin or j == park.size[0] - margin - 1:
                freeSpace.pop((i,j))
                interactiveSpace[(i,j)] = pathMark

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

    return
