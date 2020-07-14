import collections
from class_ride_and_store import Ride_and_Store as RS


object_list = collections.defaultdict()

try:
	fp = open('object_list.txt', 'r')
	for line in fp:
		line = line.strip()
		if line and line[0] != "#":
			arr = line.replace("\t", "").split(",")
			arr = arr[:1]+[int(arr[i]) for i in range(1,len(arr))]
			newObj = RS.alt_init(arr)
			# print(newObj)
			object_list[arr[0]] = newObj
finally:
	fp.close()

