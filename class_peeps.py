import random
from collections import *
from class_ride_and_store import Ride_and_Store as RS
import peeps_path_finding as PF

maxValue = 255
class Peeps:
    def __init__(self,name):
        self.id = name
        self.intensity = [random.randint(8,15),random.randrange(0,7)] ###
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
        self.headingTo = None
        self.hasMap = False
        self.position = (0,1)
        self.visited = set()
    
    def updatePosition(self,space,lst):
        if not self.headingTo:
            self.findNextRide(lst)
            return
        target = self.headingTo
        ans =  PF.main_path_finding(self,space)
        self.position = ans
        if self.position == target.position:
            print('Peep {} arrived at {}'.format(self.id,target.name))
            target.queue.append(self)
            if not target.isShop:
                self.visited.add(target.name)
            self.headingTo = None
        return 
    
    def interactWithRide(self,ride):
        print('Peep {} is on {}'.format(self.id,ride.name))
        self.happinessUpdate(ride.intensity,ride.nausea)
    
    def happinessUpdate(self,r_intensity,r_nausea):
        intensitySatisfaction = nauseaSatisfaction = 3
        maxIntensity = self.intensity[0]*100
        minIntensity = self.intensity[1]*100
        if minIntensity <= r_intensity and maxIntensity >= r_intensity:
            intensitySatisfaction -= 1
        minIntensity -= self.happiness * 2
        maxIntensity += self.happiness

        minNausea,maxNausea= self.nauseaToleranceConvert()

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
    
    def nauseaToleranceConvert(self):
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
        return minNausea,maxNausea
    
    def nauseaMaximumThresholds(self):
        if self.nauseaTolerance == 0:
            return 300
        elif self.nauseaTolerance == 1:
            return 600
        elif self.nauseaTolerance == 2:
            return 800
        else:
            return 1000

    
    def findNextRide(self,lst:list):
        def filterLst(): 
            #this code will filter unwanted ride for the peep
            #[difference] didn't deal with ride's popularity 
            #[difference] didn't consider the situation the peep is at the ride
            #[problem] using alterNumber since the number cannot fit into the object's nasuea and intensity range
            #           not ideal...?
            alterNumber = 33
            newLst = []
            maxIntensity = (min(self.intensity[0]*100,1000)+self.happiness)//alterNumber
            minIntensity = (max(self.intensity[1]*100 - self.happiness,0))//alterNumber
            maxNausea = (self.nauseaMaximumThresholds() + self.happiness)//alterNumber
            print('peeps raw intensity: {}\tmax intensity: {}\tmin intensity: {}\tmax nausea:{}'.format(self.intensity,maxIntensity,minIntensity,maxNausea))
            for mark,ride in lst:
                goodIntensity = goodNausea = False
                if maxIntensity >= ride.intensity >= minIntensity:
                    goodIntensity = True
                
                if ride.nausea <= maxNausea:
                    goodNausea = True
                # if peep's nausea > 160 it only consider gentle ride, in our case ride's nausea <10
                if self.nausea > 160 and ride.nausea >= 10:
                    goodNausea = False
                print('ride name: {}\tride intensity: {}\tride nausea: {}'.format(ride.name,ride.intensity,ride.nausea))
                
                if goodIntensity and goodNausea:
                    newLst.append((mark,ride))
            return newLst

        if  self.position == (-1,-1) or not lst:
            return
        pos = self.position
        print("old list: ",lst)
        lst = filterLst()
        print("new list: ",lst)
        #[difference] didn't contain the function makes peeps repeat visiting same ride 
        #               so we didn't consider visiting same ride at this moment
        distance = [abs(i.position[0]-pos[0])+abs(i.position[1]-pos[1]) if not i.name in self.visited else float('inf') for _,i in lst]
        if not distance:
            return
        closetRide = lst[distance.index(min(distance))][1]
        print('Peep {} new goal is {}'.format(self.id,closetRide.name))
        self.headingTo = closetRide

    def distributeTolerance(self):
        tolerance = random.randint(0,11)
        if tolerance > 0 and tolerance <= 2:
            tolerance = 1
        elif tolerance > 2 and tolerance <=5:
            tolerance =2
        else:
            tolerance = 3 
        return tolerance
