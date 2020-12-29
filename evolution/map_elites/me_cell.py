import random
class MECell:
    def __init__(self, dimensions, size, gen):
        self.dimensions = dimensions
        self.size = size
        self.pop = []
        self.gen = gen
        self.elite = None
        self.replace_count = 0
        self.challenge_count = 0

    def rank_selection(self, pop):
        # TODO order the population by fitness
        ranks = [i for i in range(0, len(pop))]
        ranks[0] = 1
        for i in range(1, len(pop)):
            ranks[i] = ranks[i-1] + i + 1
            
        for i in range(0, len(pop)):
            ranks[i] /= ranks[len(ranks) - 1]
        
        randValue = random.random()
        for i in range(0, len(ranks)): 
            if randValue <= ranks[i]:
                return pop[i]   
        return pop[pop.length - 1]
        
    def get_chromosome(self, elite_prob):
        if len(self.pop) == 0 or (self.elite != None and random.random() < elite_prob):
            return self.elite  
        return self.rank_selection(self.pop)
        
    def set_chromosome(self, chrome, replace_prob):
        self.challenge_count += 1
        if self.elite == None or chrome.fitness > self.elite.fitness:
            if self.elite != None:
                self.replace_count += 1
            self.elite = chrome
        else:
            self.elite.age += 1
            # randomly keep or throw away
            if random.random() < replace_prob:
                if len(self.pop) > self.size:
                    self.pop.remove(random.choice(self.pop))
                self.pop.append(chrome)
