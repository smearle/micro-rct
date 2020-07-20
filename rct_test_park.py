import random
from map_utility import *
from peeps_path_finding import *

def main():
    initPark(45,15)
    # place rides
    placeRide(ride[0],'&')
    placeRide(ride[1],'+')
    placeRide(ride[6],'A')
    # place path
    # place guest
    guest = peeps[0]
    updatedMap(guest.position,(1,1),humanMark)
    guest.findClosesetRide(listOfRides)
    
    printPark()
    for _ in range(10):
        print('guest: {} heading to {}'.format(guest.id,guest.headingTo))
        updatedMap(guest.position,(1,1),emptyMark)
        guest.updatePosition(freeSpace)
        updatedMap(guest.position,(1,1),humanMark)
        printPark()
    return 

main()

