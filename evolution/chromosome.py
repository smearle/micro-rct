
class Chromosome:
    def __init__(self, rct_env):
        self.env = rct_env
        self.fitness = 0

    def mutate(self):
        print('** mutating')

    def simulate(self):
        self.env.simulate()
        print('** running map')
