import random
from map_utility import *

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
    print('guest: {} heading to {}'.format(guest.id,guest.headingTo))
    printPark()
    return 

main()

