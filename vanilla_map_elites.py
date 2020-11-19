import os
import pickle
import yaml
import argparse
import random
import json
import pygame
import multiprocessing as mp
from evolution.map_elites.me_cell import MECell
from functools import partial
from micro_rct.rct_env import RCTEnv
from evolution.chromosome import Chromosome
from shutil import copyfile
from colorama import Fore, Back, Style
# colorama stuff
from colorama import init as init_colorama
init_colorama()
class MapElitesRunner:

    def __init__(self, settings_path):
        with open(settings_path) as s_file:
            settings = yaml.load(s_file, yaml.FullLoader)
        
        self.pop = []
        self.settings = settings
        self.map = {}
    
    def initialize(self):
        pop = []
        for i in range(0, self.settings.get('evolution', {}).get('population_size')):
            c = Chromosome(self.settings)
            pop.append(c)
        self.pop = pop
        
    def get_statistics(self):
        stats = []
        for i, chrome in enumerate(self.pop):
            statline = '{} | fitness: {} | dimensions: {}'.format(i, chrome.fitness, chrome.dimensions)
            stats.append(statline)
        return stats

    def assign_chromosomes(self):
        for chrome in self.pop:
            key = self.get_dimension_key(chrome.dimensions);
            if key not in self.map.keys():
                self.map[key] = MECell(chrome.dimensions, 1)
            self.map[key].set_chromosome(chrome)

    def eval_chromosome(self, index, child_conn=None):
        chrome = self.pop[index]
        # print('eval {}'.format(index))
        chrome.simulate(ticks=self.settings.get('evolution', {}).get('eval_ticks'))
        if child_conn:
            child_conn.send(chrome.fitness)

    def get_dimension_key(self, dimensions):
        return json.dumps(dimensions)
    
    def save_chromosome(self, chrome, path):
        # destroy a bunch of references to GUI since we can't render this
        with open(path, 'wb') as save_file:
            chrome.rct.rct_env.screen = None
            chrome.rct.rct_env.render_map = None
            from os import environ
            environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
            import pygame
            pygame.quit()
            # copyfile(path, path + '.bkp')
            pickle.dump(chrome, save_file)

    def save_elites(self, gen_id):
        path = self.settings.get('evolution', {}).get('save_path')
        path = os.path.join(path, '{}'.format(gen_id))
        os.makedirs(path, exist_ok=True)
        for dimension, cell in self.map.items():
            save_path = os.path.join(path, '{}.p'.format(dimension))
            self.save_chromosome(cell.elite, save_path)

    def get_grid(self):
        cells = []
        for dimen, cell in self.map.items():
            elite = cell.elite
            rep = 'Dimension: {} | Fitness: {} | Age: {}'.format(dimen, elite.fitness, elite.age)
            cells.append(rep)
        return cells

    def join_procs(self, processes):
        proc_idxs = list(processes.keys())
        for i in proc_idxs:
            # retrieve fitness scores and terminate parallel processes
            p, parent_conn = processes.pop(i)
            self.pop[i].fitness = parent_conn.recv()
            p.join()
            p.close()
    def mutate_generation(self):
        new_pop = []

        for i in range(0, self.settings.get('evolution', {}).get('population_size')):
            # take a random elite
            if random.random() <= self.settings.get('evolution', {}).get('mutation_prob'):
                # qualify for mutation
                # pick a random cell and its elite
                elite = random.choice(list(self.map.values())).elite
                child = elite.mutate()
                new_pop.append(child)
        self.pop = new_pop

    def run_generation(self, id):
        print(Fore.BLUE + '** running generation {}'.format(id))
        # run it all. RUN IT ALLLLLLL!!!!
        eval_partial = partial(self.eval_chromosome)

        if self.settings.get('parallelism', {}).get('enabled'):
            n_threads = self.settings.get('parallelism', {}).get('threads')
            processes = {}
            for i in range(0, len(self.pop)):
                # initiate parallel simulations
                parent_conn, child_conn = mp.Pipe()
                p = mp.Process(target=eval_partial, args=(i, child_conn))
                processes[i] = (p, parent_conn)
                p.start()
                if i % n_threads:
                    self.join_procs(processes)
            self.join_procs(processes)

        else:
            for i in range(0, len(self.pop)):
                self.eval_chromosome(i)
        # map elite grid
        self.assign_chromosomes()
        [print(x) for x in self.get_grid()]
        # save gen
        self.save_elites(gen_id=id)
        # run mutation
        self.mutate_generation()

class MapElitesAnalysis:
    def __init__(self, settings_path):
        with open(settings_path) as s_file:
            self.settings = yaml.load(s_file, yaml.FullLoader)

    def render_elites(self, gen_id):

        filepath = self.settings.get('evolution', {}).get('save_path')
        filepath = os.path.join(filepath, '{}'.format(gen_id))
        for file in [entry for entry in os.listdir(filepath) if entry.endswith('.p')]:
            
            with open(os.path.join(filepath, file), 'rb') as f:
                chrome = pickle.load(f)
                chrome.settings['general']['render'] = True
                chrome.rct.render_gui = True
                chrome.rct.rct_env.set_rendering(True)
                chrome.rct.rct_env.resetSim()
                chrome.rct.rct_env.render_map.render_park()
                img = chrome.rct.rct_env.screen
                img_name = '{}.png'.format(file.split('.')[0])
                # with open(os.path.join(filepath, img_name), 'w+') as save_file:
                pygame.image.save(img, os.path.join(filepath, img_name))
                    

            

def main(settings_path):
    with open(settings_path) as s_file:
        settings = yaml.load(s_file, yaml.FullLoader)
    if settings.get('evolution', {}).get('action') == 'evolve':
        runner = MapElitesRunner(settings_path)
        runner.initialize()
        print(Fore.GREEN + '** POP BREAKDOWN **')
        print(Fore.WHITE + '\n'.join(map(str, runner.get_statistics())))
        # print(runner.get_statistics())
        for i in range(settings.get('evolution', {}).get('gen_count')):
            runner.run_generation(i)
            print(Fore.WHITE + '\n'.join(map(str, runner.get_statistics())))
    else:
        analyzer = MapElitesAnalysis(settings_path)
        for generation in os.listdir(analyzer.settings.get('evolution', {}).get('save_path')):
            analyzer.render_elites(int(generation))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
