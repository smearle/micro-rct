class PeepStatus:
	def __init__(self,arr):
		self.thirst = arr[0]
		self.hunger = arr[1]
		self.nausea = arr[2]
		self.happiness = arr[3]
		self.angeriness = arr[4]
		self.energy = arr[5]

class Object:
	def __init__(self,name,size,peepReactArr,time,cost,price,position=(0,0)):
		self.name = name
		self.size = size
		self.peepReact = Peepstatus(peepReactArr) #peep status object
		self.time = time
		self.buildingcost = cost
		self.price = price
		self.position = position

try:
	fp = open('object_list.txt', 'r')
	for line in fp:
		print(line)
finally:
	fp.close()

