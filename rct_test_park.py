import random
from map_utility import *
from peeps_path_finding import *

def main():
    initPark(20,14)
    #place the path
    placePath(3)
    printPark()
    #place the ride

    #place the guest

    #testing

    return
    

# def main():
#     initPark(14,14)
#     # place rides (ride object, marks, padding)
#     placeRide(ride[0],'&',1)
#     # placeRide(ride[1],'+',1)
#     # placeRide(ride[6],'A',3)
#     # place path
#     # place guest
#     guest1,guest2 = peeps[0],peeps[1]
#     updatedMap(guest1.position,(1,1),humanMark)
#     guest1.findClosesetRide(listOfRides)
#     updatedMap(guest2.position,(1,1),humanMark)
#     guest2.findClosesetRide(listOfRides)
    
#     printPark()
#     for _ in range(5):
#         updatedHuman(guest1)
#         updatedHuman(guest2)
#         printPark()
    
#     for _,rid in listOfRides:
#         for peep in rid.queue:
#             print('peep {} on ride {}'.format(peep.id,rid.name))
#     return 
main()

