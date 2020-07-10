# class PeepStatus:
# 	def __init__(self,arr):
# 		self.thirst = arr[0]
# 		self.hunger = arr[1]
# 		self.nausea = arr[2]
# 		self.happiness = arr[3]
# 		self.angeriness = arr[4]
# 		self.energy = arr[5]

class Ride_and_Store:
	def __init__(self,name,thirst,hunger,excitement,intensity,nausea,time,cost,price,size_x,size_y,position_x=None,position_y=None):
		self.name = name
		self.size = (size_x,size_y)
		self.consume_time = time*size_y*size_x
		self.building_cost = cost*size_y*size_x
		self.price = price
		self.position = (position_x,position_y) #can assign later
		self.excitement = excitement
		self.intensity = intensity
		self.nausea = nausea
		self.thirst = thirst
		self.hunger = hunger
		self.queue = []		#queue is not implement yet
		
		#happiness: this is temperay measure
		# happiness = nausea*0.5+intensity*0.5
		# self.peepReact = PeepStatus([thirst,hunger,nausea,happiness,0,0]) #peep status object
		
	@classmethod
	def alt_init(cls,arr):
		name,thirst,hunger,excitement,intensity,nausea,time,cost,price,size_x,size_y = arr
		tmp = cls(name,thirst,hunger,excitement,intensity,nausea,time,cost,price,size_x,size_y)
		return tmp

		
	def __repr__(self):
		return "object: {}".format(self.name)
	def __str__(self):
		rtn = "id: {}\nsize: {}\tbuilding cost: {}\n".format(self.name,self.size,self.building_cost)
		rtn += "excitement: {}\tintensity: {}\tnausea: {}\tthirst: {}\thunger: {}\n".format(self.excitement,self.intensity,self.nausea,self.thirst,self.hunger)
		# rtn += "peep react: {}\n".format(self.peepReact)
		rtn += "consume time: {}\tposition: {}\n".format(self.consume_time,self.position)
		return rtn