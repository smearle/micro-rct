# import pygame
import random,sys
from class_peeps import Peeps
from rct_test_objects import object_list as ride

peeps = [Peeps(i) for i in range(3)]
peeps[0].intensity = [15,7]
peeps[1].intensity = [8,0]
ride[25].position = (5,10)
lst = [('#',ride[0]),('Q',ride[25])]


# def main():
#     tmp2 = random.randint(0,len(ride)-7)
#     print('{} intensity: {} nausea: {}'.format(ride[tmp2].name,ride[tmp2].intensity,ride[tmp2].nausea))
#     for _ in range(3):
#         tmp = random.randint(0,9)
#         print('peep: {} nauseaTolerance: {} \nbefore {}'.format(peeps[tmp].id,peeps[tmp].nauseaTolerance,peeps[tmp].happinessTarget))
#         peeps[tmp].interactWithRide(ride[1])
#         print('after {}'.format(peeps[tmp].happinessTarget))


orig_stdout = sys.stdout
f = open('testPeep.txt', 'w')
sys.stdout = f
peeps[0].position = (0,0)  
peeps[0].happiness = 0
peeps[0].nauseaTolerance = 0
for i in range(100):
    if i == 20:
        peeps[0].interactWithRide(ride[0])
    peeps[0].updateStatus(lst)
    print('peep nausea is {}'.format(peeps[0].nausea))
sys.stdout = orig_stdout
f.close()