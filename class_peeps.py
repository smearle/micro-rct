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
        self.inFirstAid = False
    
    def updatePosition(self,space,lst):
        res = []
        if self.inFirstAid:#don't update position when peep interact with first aid
            return res
        if not self.headingTo:
            res += self.findNextRide(lst)
            return res
        target = self.headingTo
        ans =  PF.main_path_finding(self,space)
        self.position = ans
        if self.position == target.position or self.position == target.enter:
            str1 = 'Peep {} arrived at {}\n'.format(self.id,target.name)
            res.append(str1)
            if target.name == 'FirstAid':
                self.inFirstAid = True
            target.queue.append(self)
            if not target.isShop:
                self.visited.add(target.name)
            self.headingTo = None
        return res

    #call every frame to update peep's current status
    # now only update nausea status
    def updateStatus(self,lst:list):
        #update nausea
        res = []
        self.updateNausea()
        if self.nausea >= 140:
            #currently not dealing with "normal sick"
            if self.nausea >= 200:
                #very sick will go to first aid
                if ((not self.headingTo) or (self.headingTo and self.headingTo.name != 'FirstAid')) and not self.inFirstAid:
                    res.append('Peep {} needs to go to first Aid\n'.format(self.id))
                    firstAids = [(mark,ride) for mark,ride in lst if ride.name == 'FirstAid']
                    res += self.findNextRide(firstAids,True)
        return res
    
    def updateNausea(self):
        newNausea = self.nausea
        newNauseaGrowth = self.nauseaTarget
        if newNausea >= newNauseaGrowth:
            newNausea = max(newNausea-4,0)
            if newNausea < newNauseaGrowth:
                newNausea = newNauseaGrowth
        else:
            newNausea = min(255,newNausea+4)
            if newNausea > newNauseaGrowth:
                newNausea = newNauseaGrowth
        
        if newNausea!=newNauseaGrowth:
            self.nausea = newNausea
        return
    
    #currently only update hapiness and Nausea Target
    def interactWithRide(self,ride):
        res = ['Peep {} is on {}\n'.format(self.id,ride.name)]
        if not ride.isShop and ride.name != 'FirstAid':     #peep on the ride
            res.append('before the ride:\n\tnausea target:{}\thappiness Target:{}\n'.format(self.nauseaTarget,self.happinessTarget))
            self.happinessUpdate(ride.intensity,ride.nausea)
            self.updateRideNauseaGrowth(ride)
            res.append('after the ride:\n\tnausea target:{}\thappiness Target:{}\n'.format(self.nauseaTarget,self.happinessTarget))

        if ride.name == 'FirstAid':
            if self.nausea <= 35:   #leave first aid when nausea below 35
                res.append('Peep {} is recovered from nausea\n'.format(self.id))
                self.inFirstAid = False
                ride.queue.remove(self)
            else:
                self.nausea -= 1
                # res.append('Peep {} nausea: {}\n'.format(self.id,self.nausea))
                self.nauseaTarget = self.nausea
        return res if len(res)>0 else []
    
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
    
    #base on:
    #   The nausea rating of the ride
    #   Their new happiness growth rate (the higher, the less nauseous)
    #   How hungry the peep is (+0% nausea at 50% hunger up to +100% nausea at 100% hunger)
    #   The peep's nausea tolerance (Final modifier: none: 100%, low: 50%, average: 25%, high: 12.5%)
    def updateRideNauseaGrowth(self,ride):
        nauseaMultiplier = max(min(256-self.happinessTarget,200),64)
        #original code is /512 but we /16 in our case
        nauseaGrowthRateChange = (ride.nausea*nauseaMultiplier)//16
        nauseaGrowthRateChange *= max(128,self.hunger)/64
        if self.nauseaTolerance == 1:
            nauseaGrowthRateChange *= 0.5
        elif self.nauseaTolerance == 2:
            nauseaGrowthRateChange *= 0.25
        elif self.nauseaTolerance == 3:
            nauseaGrowthRateChange *= 0.125
        self.nauseaTarget = min(255,self.nauseaTarget+nauseaGrowthRateChange)
        return
    
    def findNextRide(self,lst:list,specialCase=False):
        
        res = ['\nPeep {} is finding next ride\n'.format(self.id)]
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
            for mark,ride in lst:
                goodIntensity = goodNausea = False
                if maxIntensity >= ride.intensity >= minIntensity:
                    goodIntensity = True
                
                if ride.nausea <= maxNausea:
                    goodNausea = True
                # if peep's nausea > 160 it only consider gentle ride, in our case ride's nausea <10
                if self.nausea > 160 and ride.nausea >= 10:
                    goodNausea = False
                
                if goodIntensity and goodNausea and not ride.isShop:
                    newLst.append((mark,ride))
            return newLst

        if  self.position == (-1,-1) or not lst:
            res.append('the ride is not valid\n')
            return res
        pos = self.position
        if not specialCase:
            res.append('non-filter list: {}\n'.format(lst))
            lst = filterLst()
            res.append('new list: {}\n'.format(lst))
        else:
            res.append('special case list: {}\n'.format(lst))
        #[difference] didn't contain the function makes peeps repeat visiting same ride 
        #               so we didn't consider visiting same ride at this moment
        distance = [abs(i.position[0]-pos[0])+abs(i.position[1]-pos[1]) if not i.name in self.visited else float('inf') for _,i in lst]
        if not distance:
            return res
        closetRide = lst[distance.index(min(distance))][1]
        res.append('Peep {} new goal is {}'.format(self.id,closetRide.name))
        self.headingTo = closetRide
        return res

    def distributeTolerance(self):
        tolerance = random.randint(0,11)
        if tolerance > 0 and tolerance <= 2:
            tolerance = 1
        elif tolerance > 2 and tolerance <=5:
            tolerance =2
        else:
            tolerance = 3 
        return tolerance
