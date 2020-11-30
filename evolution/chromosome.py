from micro_rct.rct_env import RCTEnv
from micro_rct.gym_envs.rct_env import RCT

from micro_rct.map_utility import placePath, placeRide
from micro_rct.rct_test_objects import object_list as ride_list

import sys
sys.path.append("..")
import random

class Chromosome:
    def __init__(self, settings, env=None):
        self.settings = settings
        
        self.fitness_type = settings.get('evolution', {}).get('fitness_type')
        self.fitness = 0
        self.dimensions = {}
        self.age = 0
        for key in settings.get('evolution', {}).get('dimension_keys'):
            self.dimensions[key] = 0
        
        if env == None:
            self.rct = RCT(settings=self.settings)
            self.initialize()
        else:
            self.rct = env
        # self.calculate_dimensions()

    def initialize(self):
        self.rct.reset()

        # I don't think we need/want this
#       for i in range(random.randint(0, 3)):
#           self.rct.rand_connect()

    def mutate(self):
        child = self.clone(self.dimensions.keys())

        child.reset_sim()

        n_builds = random.randint(1, self.settings.get('evolution', {}).get('max_mutate_builds'))
        for i in range(n_builds):
            action = child.rct.action_space.sample()

            # if action['act'] == RCT.BUILDS.PATH:
            #     action['act'] = RCT.BUILDS.DEMOLISH
            child.rct.act(child.rct.action_space.sample())

        child.rct.delete_islands()
        return child


    def simulate(self, ticks=100):
        try:
            self.rct.simulate(ticks)
            self.calculate_fitness()
            self.calculate_dimensions()
        except Exception as e:
            self.fitness = -1

    def reset_sim(self):
        self.rct.resetSim()

    def clone(self, dimension_keys):
        new_env = self.rct.clone(rank=1, settings=self.settings)
        return Chromosome(self.settings, env=new_env)

    ######## CALCULATION FUNCTIONS
    def calculate_fitness(self):
        if self.fitness_type == 0:
            # random fitness
            self.fitness = random.randrange(0, 1)
        elif self.fitness_type == 1:
            # happiness fitness
            self.fitness = (0 if self.rct.rct_env.park.returnScore() < 0 else self.rct.rct_env.park.returnScore())
        elif self.fitness_type == 2:
            # park money fitness
            self.fitness = self.rct.rct_env.park.money

    def calculate_dimensions(self):
        # ride total
        if 'ride_count' in self.dimensions.keys():
            self.dimensions['ride_count'] = self.rct.rct_env.park.n_unique_rides()
        if 'happiness' in self.dimensions.keys():
            tmp = int(self.rct.rct_env.park.returnScore())
            self.dimensions['happiness'] = tmp//5 * 5
        if 'nausea' in self.dimensions.keys():
            tmp = int(self.rct.rct_env.park.returnScore(2))
            self.dimensions['nausea'] = tmp//5 * 5
        
