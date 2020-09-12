import random,sys
from class_peeps import Peeps
from rct_test_objects import object_list as ride

def generate(total,cowardRatio=0.3,braveRatio=0.3, path_finder=None):
    peeps = [Peeps(i, path_finder) for i in range(total)]
    cap1,cap2 = cowardRatio*total,(cowardRatio+braveRatio)*total

    for i in range(total):
        if i < cap1:
            peeps[i].intensity = [8,0]
        elif i < cap2:
            peeps[i].intensity = [15,7]

    return peeps
