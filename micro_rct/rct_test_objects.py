import collections
from .attraction import Attraction
import os

object_list = []
symbol_list = []
symbol_dict = {}

def create_attraction(arr):
    def init_attraction():
        return Attraction.alt_init(arr)
    return init_attraction

curr_dir = os.path.dirname(os.path.abspath(__file__))
obj_list_path = os.path.abspath(os.path.join(curr_dir, 'object_list.txt'))

with open(obj_list_path, 'r') as fp:
    i = 0
    for line in fp:
            line = line.strip()
            if line and line[0] != "#":
                arr = line.replace("\t", "").split(",")
                symbol = arr[-1]
                arr = arr[:1]+[int(arr[i]) for i in range(1,len(arr)-1)]+arr[-1:] + [i]
                #newObj = RS.alt_init(arr)
                # print(newObj)
                object_list.append(create_attraction(arr))
                symbol_list.append(symbol)
        # for i,obj in enumerate(object_list):
            # print(i,obj)
    i = 0
    for symb in symbol_list:
        symbol_dict[symb[0]] = (i, object_list[i]().name)
        i += 1
    print(symbol_dict)
    print(symbol_list)
    fp.close()

def rideNameToID(nameList):
    rtn = []
    for name in nameList:
        for i,ride in symbol_dict.values():
            if name == ride:
                rtn.append(i)
    return rtn
