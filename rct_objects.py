class PeepStatus:
	def __init__(self,arr):
		self.thirst = arr[0]
		self.hunger = arr[1]
		self.nausea = arr[2]
		self.happiness = arr[3]
		self.angeriness = arr[4]
		self.energy = arr[5]

class Object:
	def __init__(self,name,thirst,hunger,excitement,intensity,nausea,time,cost,price,position_x,position_y,size_x,size_y):
		self.name = name
		self.size = (size_x,size_y)
		self.consume_time = time*size_y*size_x
		self.building_cost = cost*size_y*size_x
		self.price = price
		self.position = (position_x,position_y)
		self.excitement = excitement
		self.intensity = intensity
		self.nausea = nausea
		#happiness: this is temperay measure
		happiness = nausea*0.5+intensity*0.5
		self.peepReact = Peepstatus([thirst,hunger,nausea,happiness,0,0]) #peep status object

try:
	fp = open('object_list.txt', 'r')
	for line in fp:
		print(line)
finally:
	fp.close()

