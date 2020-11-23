import random
class MECell:
    def __init__(self, dimensions, size):
        self.dimensions = dimensions
        self.size = size
        self.pop = []
        self.elite = None

    def rank_selection(self, pop):
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
        
    def set_chromosome(self, chrome):
        if self.elite == None or chrome.fitness > self.elite.fitness:
            self.elite = chrome
        else:
            self.elite.age += 1
            if len(self.pop) > self.size:
                self.pop.remove(random.choice(self.pop))
            self.pop.append(chrome)
