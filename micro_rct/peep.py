import random

#from peeps_path_finding import PathFinder
from .path import Path
from .pathfinding import PathFinder
from .thoughts_enums import *
from .utils.debug_utils import print_msg

#from collections import *



#PF = PathFinder()

maxValue = 255

class Peep:
    ORIGIN = (0, 1)
    def __init__(self, name, path_finder, park):
        self.id = name
        self.park = park
        self.position = self.ORIGIN
        self.type = 0 # type 0 = normal, type 1 = coward, type 2 = brave
        self.intensity = [random.randint(8,15),random.randrange(0,7)] ###
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
       #self.position = (0, 1)
        self.visited = set()
        self.inFirstAid = False
        self.time_sick = 0
        self.traversible_tiles = None
        self.curr_route = []
        self.path_finder = path_finder
        self.hasFood = False
        self.hasDrink = False
        self.n_ticks = 0
        self.thoughts = [Thought()]*5


    def updatePosition(self, space, rides_by_pos, vomitPath):
        lst = rides_by_pos.values()
        self.traversible_tiles = space
        res = []

        if self.inFirstAid:  # don't update position when peep interact with first aid
            return res

        if not self.headingTo:
            if self.hasMap:
                res += self.findNextRide(lst)
                if self.headingTo:
                    self.curr_route = self.path_finder.peep_find(self, self.park)
                else:
                    self.wander()
            else:
                self.wander()
           #return res
        target = self.headingTo

        if not self.curr_route:
            self.wander()
           #self.curr_route = [self.position]
           #self.headingTo = None

        #  when the target is not in the path_net dict,
        # could be because of deletion

#       if self.curr_route == -1:
#           print(self.park.map)
#           print(self.park.path_net)
#           raise Exception(
#               'invalid route {} to goal {} corresponding to ride at position {} with \
#                   entrance at {}'.format(self.curr_route, self.headingTo,
#                                          self.headingTo.position,
#                                          self.headingTo.entrance))
           #self.curr_route = [self.position]
           #self.headingTo = None
        self.passingBy(vomitPath)

        if self.curr_route:
            ans = self.curr_route.pop(0)

            if ans not in self.park.path_net:
                self.wander()
               #self.curr_route = []
               #self.headingTo = None
            else:
                self.position = ans

        if target is None:
            return res

        if self.position == target.position or self.position == target.entrance:
            str1 = 'Peep {} arrived at {}\n'.format(self.id, target.name)
            res.append(str1)

            if not isinstance(target, Path):

                # when peep get to kiosk we assume it will get the map for now

                if target.name == 'InformationKiosk':
                    self.hasMap = True



                if target.name == 'FirstAid':
                    self.inFirstAid = True
                target.queue.append(self)

                if not target.isShop:
                    self.visited.add(target.name)
            self.headingTo = None

        if self.position in rides_by_pos and rides_by_pos[self.position].name == 'InformationKiosk':
            self.hasMap = True

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

        self.update_thoughts()
        self.update_thoughts_Tick128(lst)
        self.n_ticks += 1

        return res


    def update_thoughts_Tick128(self, lst):
        if self.n_ticks % 8 != 0:
            return

        possible_thoughts = []
        num_thoughts = 0

        if self.energy <= 70 and self.happiness < 128:
            possible_thoughts.append(PEEP_THOUGHT_TYPE_TIRED)
            num_thoughts+=1

        if self.hunger<= 10 and not self.hasFood:
            possible_thoughts.append(PEEP_THOUGHT_TYPE_HUNGRY)
            num_thoughts+=1

        if self.thirst <= 25 and not self.hasFood:
            possible_thoughts.append(PEEP_THOUGHT_TYPE_THIRSTY)
            num_thoughts+=1

        if self.toilet >= 160:
            possible_thoughts.append(PEEP_THOUGHT_TYPE_TOILET)
            num_thoughts+=1

        if self.cash <= 9 and self.happiness >= 105 and self.energy >= 70:
            possible_thoughts.append(PEEP_THOUGHT_TYPE_RUNNING_OUT)
            num_thoughts+=1

        if possible_thoughts:
            choice = random.randint(0, num_thoughts-1)
            chosen_thought = possible_thoughts[choice]
            self.insertNewThought(chosen_thought, PEEP_THOUGHT_ITEM_NONE)

            if chosen_thought == PEEP_THOUGHT_TYPE_HUNGRY:
                self.peep_head_for_nearest_ride_type('FoodStall', lst)
            elif chosen_thought == PEEP_THOUGHT_TYPE_THIRSTY:
                self.peep_head_for_nearest_ride_type('DrinkStall', lst)
            elif chosen_thought == PEEP_THOUGHT_TYPE_TOILET:
                self.peep_head_for_nearest_ride_type('Toilet', lst)
            elif chosen_thought == PEEP_THOUGHT_TYPE_RUNNING_OUT:
                pass
                #placeholder - ATMs are not implemented yet
                #original code: peep_head_for_nearest_ride_type(this, RIDE_TYPE_CASH_MACHINE);

        elif self.nausea>=200:
            self.insertNewThought(PEEP_THOUGHT_TYPE_VERY_SICK, PEEP_THOUGHT_ITEM_NONE)
        elif self.nausea>=140:
            self.insertNewThought(PEEP_THOUGHT_TYPE_SICK, PEEP_THOUGHT_ITEM_NONE)

        return

    #adding simplified (very simplified) version of function from original code
    def peep_head_for_nearest_ride_type(self, rideType, lst):
        if self.headingTo and self.headingTo.name == rideType:
            return
        rides = [
            ride for _,ride in lst.items()

            if ride.name == rideType
        ]

        if not rides:
            return
        self.findNextRide(rides, True)

        return

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


    #adding thirst updates to hunger updates to avoid duplicate 'if' conditions
    def update_hunger(self):
        #in tick128update
        if self.n_ticks % 4 == 0:
            if self.hunger >= 15:
                self.hunger -= 15

            if self.thirst >= 5:
                self.thirst -=4
                self.toilet = min(self.toilet + 3, 255)

            #in peep_update_hunger, called in tick128update
            if self.hunger >=3:
                self.hunger -= 2
                self.EnergyTarget = min(self.energyTarget + 2, 255)
                self.toilet = min(self.toilet+1, 255)

        #in loc_68F9F3, called in tick128update
        if self.hunger < 10:
            self.hunger = max(self.hunger-2, 0)

        if self.thirst < 10:
            self.thirst = max(self.thirst-1, 0)

        #in loc_68FA89, called in tick128update
        if self.timeToConsume == 0 and self.hasFood:
            self.timeToConsume += 3

        if self.timeToConsume != 0:
            self.timeToConsume = max(self.timeToConsume-3, 0)

            if self.hasDrink:
                self.thirst = min(self.thirst + 7, 255)
            else:
                self.hunger = min(self.hunger + 7, 255)
                self.thirst = max(self.thirst - 3, 0)
                self.toilet = min(self.toilet + 2, 255)

            if self.timeToConsume == 0:
                msg = ""
                #in the original, items are stored in an array of bits/flags so this is implemented a little bit differently

                if self.hasFood and self.hasDrink:
                    #original does not compare hunger and thirst, just consumes the first item from that array

                    if self.hunger <= self.thirst:
                        self.hasFood = False
                        msg = "Peep {} is eating".format(self.id)
                    else:
                        self.hasDrink = False
                        msg = "Peep {} is drinking".format(self.id)
                else:
                    if self.hasFood:
                        msg = "Peep {} is eating".format(self.id)
                        self.hasFood = False
                    else:
                        msg = "Peep {} is drinking".format(self.id)
                        self.hasDrink = False

                if msg:
                    print_msg(msg, priority=0, verbose=self.park.settings['general']['verbose'])


    def update_toilet(self):
        if self.toilet >= 195:
            self.toilet = self.toilet - 1

    def update_happiness(self):
        ''' Update happiness, which tends toward its target.'''
        self.happiness = self.happinessTarget
       #if self.happiness >= self.happinessTarget:
       #    self.happiness = max(0, self.happiness - 1)
       #else:
       #    self.happiness = min(255, self.happiness + 1)

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

    # currently only updates according to age of each thought and to add new thoughts according to peep's needs
    # In the original code, also updates according to entering or on a ride, conditions of surroundings, leaving the park, cash running out
    def update_thoughts(self):
        add_fresh = 1
        fresh_thought = -1
        for i, thought in enumerate(self.thoughts):
            if thought.type == PEEP_THOUGHT_TYPE_NONE: 
                break
            if thought.freshness == 1:
                add_fresh = 0
                thought.fresh_timeout += 1
                if thought.fresh_timeout >=220:
                    thought.fresh_timeout = 0
                    thought.freshness += 1
                    add_fresh = 1
            elif thought.freshness > 1:
                thought.fresh_timeout+=1
                if thought.fresh_timeout == 0:
                    thought.freshness+=1
                    if thought.freshness >= 28:
                        for j in range(i+1, 5):
                            self.thoughts[j-1].type = self.thoughts[j].type
                            self.thoughts[j-1].item = self.thoughts[j].item
                            self.thoughts[j-1].freshness = self.thoughts[j].freshness
                            self.thoughts[j-1].fresh_timeout = self.thoughts[j].fresh_timeout
                        self.thoughts[-1].type = PEEP_THOUGHT_TYPE_NONE
                        self.thoughts[-1].item = PEEP_THOUGHT_ITEM_NONE
                        self.thoughts[-1].freshness = 0
                        self.thoguhts[-1].fresh_timeout = 0
            else:
                fresh_thought = i
            if add_fresh and fresh_thought != -1:
                self.thoughts[fresh_thought].freshness = 1


        return

    def insertNewThought(self, thoughtType, thoughtItem):
        if thoughtType == PEEP_THOUGHT_TYPE_NONE:
            return
        for i, thought in enumerate(self.thoughts):
            if i == 0: 
                continue
            if thought.type == PEEP_THOUGHT_TYPE_NONE:
                break
            if thought.type == thoughtType:
                thought.type = self.thoughts[i-1].type
                thought.item = self.thoughts[i-1].item
                break
            thought.type = self.thoughts[i-1].type
            thought.item = self.thoughts[i-1].item
        self.thoughts[0].type = thoughtType
        self.thoughts[0].item = thoughtItem
        self.thoughts[0].freshness = 0
        self.thoughts[0].fresh_timeout = 0

        msg = "Peep {} is thinking {}".format(self.id, str(thoughtType))
        print_msg(msg, priority=0, verbose=self.park.settings['general']['verbose'])


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

            if self.hunger > 75:
                self.insertNewThought(PEEP_THOUGHT_TYPE_NOT_HUNGRY, PEEP_THOUGHT_ITEM_NONE)
            else:
                self.hasFood = True
            # removing the below, adding timeToConsume update to update_hunger
            # in OpenRCT2 this is added when timeToConsume==0 and peep.hasFood
            # self.timeToConsume += 3

        if ride.name == 'DrinkStall':
            #           print('peep {} has acquired food'.format(self.id))

            if self.thirst > 75:
                self.insertNewThought(PEEP_THOUGHT_TYPE_NOT_THIRSTY, PEEP_THOUGHT_ITEM_NONE)
            else:
                self.hasDrink = True

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
        if self.position not in self.park.path_net:
            return
        current_tile = self.park.path_net[self.position]
        traversible_tiles = current_tile.get_junctions(self.park.path_net)

        if len(traversible_tiles) == 0:
            self.headingTo = None
        else:
            goal = random.choice(traversible_tiles)
            # FIXME: do not create new path object every time
            self.headingTo = goal

            self.curr_route = self.path_finder.peep_find(self, self.park)
