class Path:
    def __init__(self, position):
        self.name = 'path'
        self.position = position
        self.entrance = position

class Attraction:
    def __init__(self, name, thirst, hunger, toilet, excitement, intensity, nausea, time, cost, price, size_x, size_y,
            mark, position_x=0, position_y=0, ride_i=-1):
        self.name = name
        self.mark = mark
        if thirst!=0 or hunger!=0 or toilet!=0 or name == 'FirstAid' or name =='InformationKiosk' or name=='Shop':
                self.isShop = True
        else:
                self.isShop = False
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
        self.entrance = (0,0) #current just place the enterence at the top left
        self.exit = (size_x-1,size_y-1) #current just place the exit at the bottom right
        self.queue = []		#append peep here
        self.ride_i = ride_i

    @classmethod
    def alt_init(cls,arr):
        name,thirst,hunger,toilet,excitement,intensity,nausea,time,cost,price,size_x,size_y,mark, ride_i = arr
        tmp = cls(name,thirst,hunger,toilet,excitement,intensity,nausea,time,cost,price,size_x,size_y, mark, ride_i)
        return tmp


    def __repr__(self):
        return "object: {}".format(self.name)
    def __str__(self):
        rtn = "id: {}\nsize: {}\tbuilding cost: {}\n".format(self.name,self.size,self.building_cost)
        rtn += "excitement: {}\tintensity: {}\tnausea: {}\nthirst: {}\thunger: {}\ttoilet: {}\n".format(self.excitement,self.intensity,self.nausea,self.thirst,self.hunger,self.toilet)
        # rtn += "peep react: {}\n".format(self.peepReact)
        rtn += "consume time: {}\tposition: {}\n".format(self.consume_time,self.position)
        return rtn
