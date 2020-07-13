class Ride_and_Store:
	def __init__(self,name,thirst,hunger,toilet,excitement,intensity,nausea,time,cost,price,size_x,size_y,position_x=None,position_y=None):
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
		self.toilet = toilet
		self.hunger = hunger
		self.queue = []		#queue is not implement yet
		
	@classmethod
	def alt_init(cls,arr):
		name,thirst,hunger,toilet,excitement,intensity,nausea,time,cost,price,size_x,size_y = arr
		tmp = cls(name,thirst,hunger,toilet,excitement,intensity,nausea,time,cost,price,size_x,size_y)
		return tmp

		
	def __repr__(self):
		return "object: {}".format(self.name)
	def __str__(self):
		rtn = "id: {}\nsize: {}\tbuilding cost: {}\n".format(self.name,self.size,self.building_cost)
		rtn += "excitement: {}\tintensity: {}\tnausea: {}\nthirst: {}\thunger: {}\ttoilet: {}\n".format(self.excitement,self.intensity,self.nausea,self.thirst,self.hunger,self.toilet)
		# rtn += "peep react: {}\n".format(self.peepReact)
		rtn += "consume time: {}\tposition: {}\n".format(self.consume_time,self.position)
		return rtn