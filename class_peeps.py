import random
import class_ride_and_store as RS

maxValue = 255
class Peeps:
    def __init__(self,name,posX=None,posY=None):
        self.id = name
        self.intensity = [random.randint(8,15),random.randrange(0,7)]
        self.happiness = 128
        self.happinessTarget = 128
        self.nausea = 0
        self.nauseaTarget = 0
        self.hunger = random.randint(0,maxValue)
        self.nauseaTolerance = self.distributeTolerance()
        self.thirst = random.randint(0,maxValue)
        self.angriness = 0
        self.toilet = 0
        self.timeToConsume = 0
        self.cash = random.randint(400,600)
        self.energy = random.randint(65,128)
        self.energyTarget = self.energy
        self.timeInPark = -1
        self.headingTo = (posX,posY)
        self.hasMap = False
    
    def interactWithRide(self,ride):
        self.happinessUpdate(ride.intensity,ride.nausea)
    
    def happinessUpdate(self,r_intensity,r_nausea):
        intensitySatisfaction = nauseaSatisfaction = 3
        maxIntensity = self.intensity[0]*100
        minIntensity = self.intensity[1]*100
        if minIntensity <= r_intensity and maxIntensity >= r_intensity:
            intensitySatisfaction -= 1
        minIntensity -= self.happiness * 2
        maxIntensity += self.happiness
        if self.nauseaTolerance == 0:
            minNausea = 0
            maxNausea = 10
        elif self.nauseaTolerance == 1:
            minNausea = 0
            maxNausea = 20
        elif self.nauseaTolerance == 2:
            minNausea = 20
            maxNausea = 35
        else:
            minNausea = 25
            maxNausea = 55
        if minNausea <= r_nausea and maxNausea >= r_nausea:
            nauseaSatisfaction -= 1
        for _ in range(2):
            minNausea -= self.happiness*2
            maxNausea += self.happiness
            if minNausea <= r_nausea and maxNausea >= r_nausea:
                nauseaSatisfaction -= 1
        highestSatisfaction = max(intensitySatisfaction,nauseaSatisfaction)
        lowestSatisfaction = min(nauseaSatisfaction,intensitySatisfaction)
        if highestSatisfaction == 0:
            self.happinessTarget = min(self.happinessTarget+70,maxValue)
        elif highestSatisfaction == 1:
            if lowestSatisfaction == 0:
                self.happinessTarget = min(self.happinessTarget+50,maxValue)
            if lowestSatisfaction == 1:
                self.happinessTarget = min(self.happinessTarget+30,maxValue)
        elif highestSatisfaction == 2:
            if lowestSatisfaction == 0:
                self.happinessTarget = min(self.happinessTarget+35,maxValue)
            if lowestSatisfaction == 1:
                self.happinessTarget = min(self.happinessTarget+20,maxValue)
            if lowestSatisfaction == 2:
                self.happinessTarget = min(self.happinessTarget+10,maxValue)
        elif highestSatisfaction == 3:
            if lowestSatisfaction == 0:
                self.happinessTarget = min(self.happinessTarget-35,maxValue)
            if lowestSatisfaction == 1:
                self.happinessTarget = min(self.happinessTarget-50,maxValue)
            else:
                self.happinessTarget = min(self.happinessTarget-60,maxValue)

    def distributeTolerance(self):
        tolerance = random.randint(0,11)
        if tolerance > 0 and tolerance <= 2:
            tolerance = 1
        elif tolerance > 2 and tolerance <=5:
            tolerance =2
        else:
            tolerance = 3 
        return tolerance
