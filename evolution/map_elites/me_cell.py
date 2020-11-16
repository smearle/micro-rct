import random
class MECell:
    def __init__(self, dimensions, size):
        self.dimensions = dimensions
        self.size = size
        self.pop = []
        self.elite = None

    def rank_selection(pop):
        ranks = [i for i in range(0, len(pop.length))]
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
        

    # public Chromosome getChromosome(double eliteProb) {
	# Chromosome elite = this.getElite()
	# Chromosome[] infeasible = this.getInfeasible(false)
	# if(infeasible.length == 0 | | (elite != null & & this._rnd.nextDouble() < eliteProb)) {
	#     return elite
    #     }
	# return this.rankSelection(infeasible)
    # }
    def set_chromosome(self, chrome):
        if self.elite == None or chrome.fitness > self.elite.fitness:
            self.elite = chrome
        else:
            self.elite.age += 1