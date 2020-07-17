# import pygame
import random
import class_peeps as CP
from rct_test_objects import object_list as ride

peeps = [CP.Peeps(i) for i in range(10)]
# print(vars(peeps[0]))

def main():
    tmp2 = random.randint(0,len(ride)-7)
    print('select ride {} intensity: {} nausea: {}'.format(ride[tmp2].name,ride[tmp2].intensity,ride[tmp2].nausea))
    for _ in range(3):
        tmp = random.randint(0,9)
        print('peep: {} nauseaTolerance: {} \nbefore {}'.format(peeps[tmp].id,peeps[tmp].nauseaTolerance,peeps[tmp].happinessTarget))
        peeps[tmp].interactWithRide(ride[1])
        print('after {}'.format(peeps[tmp].happinessTarget))

main()