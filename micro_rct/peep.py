import random
#from collections import *

#from peeps_path_finding import PathFinder
from .path import Path, PathFinder

#PF = PathFinder()

#adding thought types here. Could also just do them as ints or as strings. 
#original game also creates a struct for thoughts, not sure that's necessary here.
PEEP_THOUGHT_TYPE_SICK = 2             #"I feel sick"
PEEP_THOUGHT_TYPE_VERY_SICK = 3        #"I feel very sick"
PEEP_THOUGHT_TYPE_TIRED = 19           #"I'm tired"
PEEP_THOUGHT_TYPE_HUNGRY = 20          #"I'm hungry"
PEEP_THOUGHT_TYPE_THIRSTY = 21         #"I'm thirsty"
PEEP_THOUGHT_TYPE_TOILET = 22          #"I need to go to the toilet"
PEEP_THOUGHT_TYPE_NONE = 255

maxValue = 255


class Peep:
    def __init__(self, name, path_finder, park):
        self.id = name
        self.park = park
        self.intensity = [random.randint(8, 15), random.randrange(0, 7)]
        self.happiness = 128
        self.happinessTarget = 128
        self.nausea = 0
        self.nauseaTarget = 0
        self.hunger = random.randint(0, maxValue)
        self.nauseaTolerance = self.distributeTolerance()
        self.thirst = random.randint(0, maxValue)
        self.angriness = 0
        self.toilet = 0
        self.timeToConsume = 0
        self.disgustingCount = 0
        self.cash = random.randint(400, 600)
        self.energy = random.randint(65, 128)
        self.energyTarget = self.energy
        self.timeInPark = -1
        self.headingTo = None
        self.hasMap = False
        self.position = (0, 1)
        self.visited = set()
        self.inFirstAid = False
        self.time_sick = 0
        self.traversible_tiles = None
        self.curr_route = []
        self.path_finder = path_finder
        self.hasFood = False
        #not implementing thoughts as a class yet, just a list of thought types and their age
        self.thoughts = [[PEEP_THOUGHT_TYPE_NONE, 0]]*5


    def updatePosition(self, space, rides_by_pos, vomitPath):
        lst = rides_by_pos.values()
        self.traversible_tiles = space
        res = []

        if self.inFirstAid:  # don't update position when peep interact with first aid
            return res

        if not self.headingTo: 
            res += self.findNextRide(lst)

            return res
        target = self.headingTo
        #       ans =  PF.main_path_finding(self,space)
        if not self.curr_route:
            self.curr_route = self.path_finder.find(self)
        else:
            #           print('REUSING ROUTE')
            pass

        if not self.curr_route:
            self.curr_route = [self.position]
            self.headingTo = None

        #  when the target is not in the path_net dict,
        # could be because of deletion
        if self.curr_route == -1:
            print(self.park.printPark())
            print(self.park.path_net)
            raise Exception(
                'invalid route {} to goal {} corresponding to ride at position {} with \
                    entrance at {}'.format(self.curr_route, self.headingTo,
                                           self.headingTo.position,
                                           self.headingTo.entrance))
           #self.curr_route = [self.position]
           #self.headingTo = None
        ans = self.curr_route.pop(0)

        self.passingBy(vomitPath)

        self.position = ans

        if self.position == target.position or self.position == target.entrance:
            str1 = 'Peep {} arrived at {}\n'.format(self.id, target.name)
            res.append(str1)

            if not isinstance(target, Path):

                if target.name == 'FirstAid':
                    self.inFirstAid = True
                target.queue.append(self)

                if not target.isShop:
                    self.visited.add(target.name)
            self.headingTo = None

        return res

    # call every frame to update peep's current status
    # now only update nausea status
    def updateStatus(self, lst: list):
        # update nausea
        res = []
        self.update_nausea()

        res = self.nauseaCondition(lst)

        self.update_happiness()
        self.update_hunger()
        self.update_toilet()

        return res

    def passingBy(self, vomitPath):
        sickCount = 0

        for vo_x, vo_y in vomitPath:
            dis = abs(vo_x - self.position[0]) + abs(vo_y - self.position[1])

            if dis <= 16:
                sickCount += 1

        # I am copying original code, I have no idea what is it about...
        disgusting_time = self.disgustingCount & 0xC0
        disgusting_count = ((self.disgustingCount & 0xF) << 2) | sickCount
        self.disgustingCount = disgusting_count | disgusting_time

        if disgusting_time & 0xc0 and random.randint(0,
                                                     65534) & 0xffff <= 4369:
            self.disgustingCount -= 0x40
        else:
            totalSick = 0

            for i in range(3):
                totalSick += (disgusting_count >> (2 * i)) & 0x3

            if totalSick >= 3 and random.randint(0, 65534) & 0xffff <= 10922:
                self.happinessTarget = max(0, self.happinessTarget - 17)
                self.disgustingCount |= 0xc0

        return

    def nauseaCondition(self, lst: list):
        res = []

        if self.nausea > 128:
            # in the orginal code peep will have chance to throw up when walking with nausea>128
            # since current peeps will always be walking we will run this code everytime we update
            # peeps cannot create vomit litter at the same location
            chance = random.randint(0, maxValue)

            if chance <= (
                    self.nausea -
                    128) / 2:  # the higher nausea the higher chance to vomit
                self.vomit()

        if self.nausea >= 140:
            # currently not dealing with "normal sick"

            if self.nausea >= 200:
                    # very sick will go to first aid

                if ((not self.headingTo) or
                    (self.headingTo and self.headingTo.name != 'FirstAid')
                    ) and not self.inFirstAid:
                    res.append('Peep {} needs to go to first Aid'.format(
                        self.id))
                    firstAids = [
                        ride for _, ride in lst.items()
                        if ride.name == 'FirstAid'
                    ]
                    res += self.findNextRide(firstAids, True)
        
        #in original code, some updates to thoughts are inside tick128UpdateGuest and some are in a separate update_thoughts function. Keeping updates together for clarity.
        self.update_thoughts()

        return res

    def vomit(self):
        #       print('Peep {} vomits '.format(self.id))
        self.nauseaTarget /= 2
        self.hunger /= 2

        if self.nausea > 30:
            self.nausea -= 30
        else:
            self.nausea = 0
        self.park.add_vomit(self.position)
        # self.headingTo = None

    def update_hunger(self):
        # TODO: I think this is prompted by a particular thought? "PEEP_FLAGS_HUNGER"
        # if self.hunger >= 15:
        #    self.hunger -= 15
        # TODO: need thoughts
        # if self.hunger <= 10 and not self.hasFood:
        #    # add possible hunger thought
        if self.hunger < 10:
            self.hunger = max(self.hunger - 1, 0)

        if self.hasFood:
            self.hunger = min(self.hunger + 7, 255)
            self.thirst = max(self.thirst - 3, 0)
            self.toilet = min(self.toilet + 2, 255)
            self.timeToConsume -= 1

            if self.timeToConsume == 0:
                self.hasFood = False

    def update_toilet(self):
        if self.toilet >= 195:
            self.toilet = self.toilet - 1

    def update_happiness(self):
        ''' Update happiness, which tends toward its target.'''

        if self.happiness >= self.happinessTarget:
            self.happiness = max(0, self.happiness - 1)
        else:
            self.happiness = min(255, self.happiness + 1)

        return

    def update_nausea(self):
        newNausea = self.nausea
        newNauseaGrowth = self.nauseaTarget

        # increment nausea toward target

        if newNausea >= newNauseaGrowth:
            newNausea = max(newNausea - 4, 0)

            # adjust if we've passed the target

            if newNausea < newNauseaGrowth:
                newNausea = newNauseaGrowth
        else:
            newNausea = min(255, newNausea + 4)

            if newNausea > newNauseaGrowth:
                newNausea = newNauseaGrowth

        if newNausea != newNauseaGrowth:
            self.nausea = newNausea

        # TODO: this is in the original code and should probably be in ours as well


#       self.nauseaTarget = max(self.nauseaTarget - 2, 0)

        return

    # MARIA: currently only updates according to age of each thought and to add new thoughts according to peep's needs
    # combining updates from original code's Tick128UpdateGuest and update_thoughts. 
    # In the original code, also updates according to entering or on a ride, conditions of surroundings, leaving the park, cash running out
    def update_thoughts(self):
        for i in range(5):
            #print(self.thoughts[i])
            self.thoughts[i][1]+=1
            if self.thoughts[i][1]>=6900:
                self.thoughts.pop(i)
                self.thoughts.append([PEEP_THOUGHT_TYPE_NONE,0])

        #not adding call to return if peep is at first aid or on a ride.
        possible_thoughts = []

        if self.energy <= 70 and self.happiness < 128:
            possible_thoughts.append(PEEP_THOUGHT_TYPE_TIRED)
        if self.hunger<= 10: #and not self.hasFood
            possible_thoughts.append(PEEP_THOUGHT_TYPE_HUNGRY)
        if self.thirst <= 25: #and not self.hasFood
            possible_thoughts.append(PEEP_THOUGHT_TYPE_THIRSTY)
        if self.toilet >= 160:
            possible_thoughts.append(PEEP_THOUGHT_TYPE_TOILET)
        #original game also has check on money, to insert thought type running out

        if possible_thoughts:
            choice = random.randint(0, len(possible_thoughts)-1)
            chosen_thought = possible_thoughts[choice]
            self.insertNewThought(chosen_thought)
        
        #original game also has switch for chosen thought, takes action based on that thought
        
        elif self.nausea>=200:
            self.insertNewThought(PEEP_THOUGHT_TYPE_VERY_SICK)
        elif self.nausea>=140:
            self.insertNewThought(PEEP_THOUGHT_TYPE_SICK)

        return

    def insertNewThought(self, thoughtType):
        self.thoughts.insert(0, [thoughtType, 0])
        self.thoughts.pop(5)


    #currently only update hapiness and Nausea Target
    def interactWithRide(self,ride):
        res = ['Peep {} is on {}\n'.format(self.id,ride.name)]

        if not ride.isShop and ride.name != 'FirstAid':  # peep on the ride
            res.append(
                'before the ride:\n\tnausea target:{}\thappiness Target:{}\n'.
                format(self.nauseaTarget, self.happinessTarget))
            self.happinessTrgUpdate(ride.intensity, ride.nausea)
            self.updateRideNauseaGrowth(ride)
            res.append(
                'after the ride:\n\tnausea target:{}\thappiness Target:{}\n'.
                format(self.nauseaTarget, self.happinessTarget))

        if ride.name == 'FirstAid':
            if self.nausea <= 35:  # leave first aid when nausea below 35
                res.append('Peep {} is recovered from nausea\n'.format(
                    self.id))
                self.inFirstAid = False
                ride.queue.remove(self)
            else:
                self.nausea -= 1
                # res.append('Peep {} nausea: {}\n'.format(self.id,self.nausea))
                self.nauseaTarget = self.nausea

        if ride.name == 'FoodStall':
            #           print('peep {} has acquired food'.format(self.id))
            self.hasFood = True
            # in OpenRCT2 this is added when timeToConsume==0 and peep.hasFood
            self.timeToConsume = 3

        return res if len(res) > 0 else []

    def happinessTrgUpdate(self, r_intensity, r_nausea):
        intensitySatisfaction = nauseaSatisfaction = 3
        maxIntensity = self.intensity[0] * 100
        minIntensity = self.intensity[1] * 100

        if minIntensity <= r_intensity and maxIntensity >= r_intensity:
            intensitySatisfaction -= 1
        minIntensity -= self.happiness * 2
        maxIntensity += self.happiness

        minNausea, maxNausea = self.nauseaToleranceConvert()

        if minNausea <= r_nausea and maxNausea >= r_nausea:
            nauseaSatisfaction -= 1

        for _ in range(2):
            minNausea -= self.happiness * 2
            maxNausea += self.happiness

            if minNausea <= r_nausea and maxNausea >= r_nausea:
                nauseaSatisfaction -= 1
        highestSatisfaction = max(intensitySatisfaction, nauseaSatisfaction)
        lowestSatisfaction = min(nauseaSatisfaction, intensitySatisfaction)

        if highestSatisfaction == 0:
            self.happinessTarget = min(self.happinessTarget + 70, maxValue)
        elif highestSatisfaction == 1:
            if lowestSatisfaction == 0:
                self.happinessTarget = min(self.happinessTarget + 50, maxValue)

            if lowestSatisfaction == 1:
                self.happinessTarget = min(self.happinessTarget + 30, maxValue)
        elif highestSatisfaction == 2:
            if lowestSatisfaction == 0:
                self.happinessTarget = min(self.happinessTarget + 35, maxValue)

            if lowestSatisfaction == 1:
                self.happinessTarget = min(self.happinessTarget + 20, maxValue)

            if lowestSatisfaction == 2:
                self.happinessTarget = min(self.happinessTarget + 10, maxValue)
        elif highestSatisfaction == 3:
            if lowestSatisfaction == 0:
                self.happinessTarget = min(self.happinessTarget - 35, maxValue)

            if lowestSatisfaction == 1:
                self.happinessTarget = min(self.happinessTarget - 50, maxValue)
            else:
                self.happinessTarget = min(self.happinessTarget - 60, maxValue)

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

        return minNausea, maxNausea

    def nauseaMaximumThresholds(self):
        if self.nauseaTolerance == 0:
            return 300
        elif self.nauseaTolerance == 1:
            return 600
        elif self.nauseaTolerance == 2:
            return 800
        else:
            return 1000

    # base on:
    #   The nausea rating of the ride
    #   Their new happiness growth rate (the higher, the less nauseous)
    #   How hungry the peep is (+0% nausea at 50% hunger up to +100% nausea at 100% hunger)
    #   The peep's nausea tolerance (Final modifier: none: 100%, low: 50%, average: 25%, high: 12.5%)
    def updateRideNauseaGrowth(self, ride):
        nauseaMultiplier = max(min(256 - self.happinessTarget, 200), 64)
        # original code is /512 but we /16 in our case
        nauseaGrowthRateChange = (ride.nausea * nauseaMultiplier) // 16
        nauseaGrowthRateChange *= max(128, self.hunger) / 64

        if self.nauseaTolerance == 1:
            nauseaGrowthRateChange *= 0.5
        elif self.nauseaTolerance == 2:
            nauseaGrowthRateChange *= 0.25
        elif self.nauseaTolerance == 3:
            nauseaGrowthRateChange *= 0.125
        self.nauseaTarget = min(255,
                                self.nauseaTarget + nauseaGrowthRateChange)

        return

    def findNextRide(self, lst: list, specialCase=False):

        res = ['\nPeep {} is finding next ride\n'.format(self.id)]

        def filterLst():
            # this code will filter unwanted ride for the peep
            # [difference] didn't deal with ride's popularity
            # [difference] didn't consider the situation the peep is at the ride
            # [problem] using alterNumber since the number cannot fit into the object's nasuea and intensity range
            #           not ideal...?
            alterNumber = 33
            newLst = []
            maxIntensity = (min(self.intensity[0] * 100, 1000) +
                            self.happiness) // alterNumber
            minIntensity = (max(self.intensity[1] * 100 - self.happiness,
                                0)) // alterNumber
            maxNausea = (self.nauseaMaximumThresholds() +
                         self.happiness) // alterNumber

            for ride in lst:
                goodIntensity = goodNausea = False

                if maxIntensity >= ride.intensity >= minIntensity:
                    goodIntensity = True

                if ride.nausea <= maxNausea:
                    goodNausea = True
                # if peep's nausea > 160 it only consider gentle ride, in our case ride's nausea <10

                if self.nausea > 160 and ride.nausea >= 10:
                    goodNausea = False

                if goodIntensity and goodNausea and not ride.isShop:
                    newLst.append((ride))

                # FIXME: ad hoc to test food-eating functionality. How is this selected in OpenRCT2?

                if ride.name == 'FoodStall' and self.hunger < 50:
                    newLst.append((ride))

            return newLst

        if self.position == (-1, -1) or not lst:
            res.append('the ride is not valid\n')
            self.wander()

            return res
        pos = self.position

        if not specialCase:
            res.append('non-filter list: {}\n'.format(lst))
            lst = filterLst()
            res.append('new list: {}\n'.format(lst))
        else:
            res.append('special case list: {}\n'.format(lst))
        # [difference] didn't contain the function makes peeps repeat visiting same ride
        #               so we didn't consider visiting same ride at this moment
        distance = [
            abs(i.entrance[0] - pos[0]) + abs(i.entrance[1] - pos[1])
            if not i.name in self.visited else float('inf') for i in lst
        ]

        if not distance or lst == [] or distance == float('inf'):
            res.append('Peep {} finds no satisfactory ride.'.format(self.id))

            if self.traversible_tiles is not None:
                # FIXME: Make this more true to OpenRCT2
                self.wander()
                pass
            else:
                res.append('no traversible tiles')

            return res
        closestRide = lst[distance.index(min(distance))]
        res.append('Peep {} new goal is {} at {}'.format(
            self.id, closestRide.name, closestRide.entrance))
        self.headingTo = closestRide

        return res

    def distributeTolerance(self):
        tolerance = random.randint(0, 11)

        if 2 >= tolerance > 0:
            tolerance = 1
        elif 5 >= tolerance > 2:
            tolerance = 2
        else:
            tolerance = 3

        return tolerance

    def wander(self):
        '''Pick a random destination.'''
        traversible_tiles = self.park.path_net
        #print('traversible tiles: {}'.format(traversible_tiles))
        if len(traversible_tiles) == 0:
            self.headingTo = self.position
        else:
            goal = random.choice(list(traversible_tiles.keys()))
            # FIXME: do not create new path object every time
            self.headingTo = self.park.path_net[goal]
