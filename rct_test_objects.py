import collections
from class_ride_and_store import Ride_and_Store as RS


object_list = []
symbol_list = []

try:
	fp = open('object_list.txt', 'r')
	for line in fp:
		line = line.strip()
		if line and line[0] != "#":
                    arr = line.replace("\t", "").split(",")
                    symbol = arr[-1]
                    arr = arr[:1]+[int(arr[i]) for i in range(1,len(arr)-1)]
                    newObj = RS.alt_init(arr)
                    # print(newObj)
                    object_list.append(newObj)
                    symbol_list.append(symbol)
	# for i,obj in enumerate(object_list):
            # print(i,obj)
finally:
	fp.close()
