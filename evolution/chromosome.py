import sys
sys.path.append("..")
import random
from micro_rct.rct_env import RCTEnv
class Chromosome:
    def __init__(self, settings, env=None):
        self.settings = settings
        
        self.fitness_type = settings.get('evolution', {}).get('fitness_type')
        self.fitness = 0
        self.dimensions = {}
        for key in settings.get('evolution', {}).get('dimension_keys'):
            self.dimensions[key] = 0
        
        if env == None:
            self.env = RCTEnv(self.settings)
            self.initialize()
        else:
            self.env = env
        self.calculate_dimensions()

    def initialize(self):
        self.env.reset()
        
    def mutate(self):
        # TODO
        print('** mutating')
        self.calculate_dimensions()

    def simulate(self):
        self.env.simulate()
        self.calculate_fitness()

    def reset_sim(self):
        self.env.resetSim()

    def clone(self, dimension_keys):
        clone_park = self.env.park.clone()
        new_env = RCTEnv(settings, clone_park)
        return Chromosome(self.settings, dimension_keys, fitness_type=self.fitness_type, env=new_env)


    ######## CALCULATION FUNCTIONS
    def calculate_fitness(self):
        if self.fitness_type == 0:
            # random fitness
            self.fitness = random.randrange(0, 1)
        elif self.fitness_type == 1:
            # happiness fitness
            avg_happiness = 0
            for peep in self.env.park.peepsList:
                avg_happiness += peep.happiness
            self.fitness = avg_happiness / len(self.peepsList)

    def calculate_dimensions(self):
        # ride total
        if 'ride_count' in self.dimensions.keys():
            self.dimensions['ride_count'] = len(self.env.park.rides_by_pos.keys())
        if 'happiness' in self.dimensions.keys():
            avg_happiness = 0
            for peep in self.env.park.peepsList:
                avg_happiness += peep.happiness
            self.dimensions['happiness'] = avg_happiness / len(self.peepsList)
             
    
    ####### UTILITY FUNCTIONS

