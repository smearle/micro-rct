import random,sys
from map_utility import *
from peeps_path_finding import *
from park import Park

peeps = generate(5,0.2,0.2)

def main():
    park = initPark(40,20)
    #place the path
    placePath(park, 3)
    park.printPark()
    #place the ride (ride object, marks)
    placeRide(park, ride[0],'&')
    placeRide(park, ride[1],'T')
    placeRide(park, ride[6],'C')
    placeRide(park, ride[7],'G')
    placeRide(park, ride[25],'F')#first aid
    park, park.printPark()
    #place the guest

    for p in peeps:
        res = park.updateHuman(p)

        for line in res:
            print(line)
    park, park.printPark()
    #testing
    frame = 0

    for _ in range(200):
        frame +=1
        park.update(frame)

    return

orig_stdout = sys.stdout
f = open('out.txt', 'w')
sys.stdout = f
main()
sys.stdout = orig_stdout
f.close()

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
