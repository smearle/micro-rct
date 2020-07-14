import random
import class_ride_and_store as RS
class Peeps:
    def __init__(self,name,posX=None,posY=None):
        self.id = name
        self.intensity = [random.randint(8,15),random.randrange(0,7)]
        self.happiness = 128
        self.happinessTarget = 128
        self.nausea = 0
        self.nauseaTarget = 0
        self.hunger = random.randint(0,255)
        self.nauseaTolerance = self.distributeTolerance()
        self.thirst = random.randint(0,255)
        self.angriness = 0
        self.toilet = 0
        self.timeToConsume = 0
        self.cash = random.randint(400,600)
        self.energy = random.randint(65,128)
        self.energyTarget = self.energy
        self.timeInPark = -1
        self.headingTo = (posX,posY)
        self.hasMap = False
    
    # def updateHappiness(self,intensity,nausea):

    def distributeTolerance(self):
        tolerance = random.randint(0,11)
        if tolerance > 0 and tolerance <= 2:
            tolerance = 1
        elif tolerance > 2 and tolerance <=5:
            tolerance =2
        else:
            tolerance = 3 
        return tolerance
