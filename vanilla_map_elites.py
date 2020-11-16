import yaml
import argparse
import random
import json
import multiprocessing as mp
from evolution.map_elites.me_cell import MECell
from functools import partial
from micro_rct.rct_env import RCTEnv
from evolution.chromosome import Chromosome

class MapElitesRunner:

    def __init__(self, settings_path):
        with open(settings_path) as s_file:
            settings = yaml.load(s_file, yaml.FullLoader)
        pop = []
        for i in range(0, settings.get('evolution', {}).get('population_size')):
            c = Chromosome(settings)
            pop.append(c)
        self.pop = pop
        self.settings = settings
        self.map = {}

    def get_statistics(self):
        stats = ''
        for i, chrome in enumerate(self.pop):
            statline = '{} | fitness: {} | dimensions: {}'.format(i, chrome.fitness, chrome.dimensions)
            stats += statline + '\n'
        return stats

    def assign_chromosomes(self):
        for chrome in self.pop:
            key = self.get_dimension_key(chrome.dimensions);
            if key not in self.map.keys():
                self.map[key] = MECell(chrome.dimensions, 1)
            self.map[key].set_chromosome(chrome)

    def eval_chromosome(self, index):
        chrome = self.pop[index]
        # print('eval {}'.format(index))
        chrome.simulate(ticks=self.settings.get('evolution', {}).get('eval_ticks'))

    def get_dimension_key(self, dimensions):
        return json.dumps(dimensions)

    def get_grid(self):
        cells = []
        for dimen, cell in self.map.items():
            elite = cell.elite
            rep = 'Dimension: {} | Fitness: {} | Age: {}'.format(dimen, elite.fitness, elite.age)
            cells.append(rep)
        return cells

    def run_generation(self, id):
        print('** running generation {}'.format(id))
        # run it all. RUN IT ALLLLLLL!!!!
        eval_partial = partial(self.eval_chromosome)

        if self.settings.get('parallelism', {}).get('enabled'):
            pool = mp.Pool(self.settings.get('parallelism', {}).get('threads'))
            pool.map(eval_partial, [i for i in range(0, len(self.pop))])

            pool.close()
            pool.join()
        else:
            for i in range(0, len(self.pop)):
                self.eval_chromosome(i)
        # map elite grid
        self.assign_chromosomes()
        [print(x) for x in self.get_grid()]
        # run mutation
        new_pop = []
        for i in range(0, self.settings.get('evolution', {}).get('population_size')):
            # take a random elite
            if random.random() <= self.settings.get('evolution', {}).get('mutation_prob'):
                # qualify for mutation
                print('mutate!')

def main(settings_path):
    with open(settings_path) as s_file:
        settings = yaml.load(s_file, yaml.FullLoader)
    runner = MapElitesRunner(settings_path)
    print('** POP BREAKDOWN **')
    print(runner.get_statistics())
    for i in range(settings.get('evolution', {}).get('gen_count')):
        runner.run_generation(i)
        print(runner.get_statistics())

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
