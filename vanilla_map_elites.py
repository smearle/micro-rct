import os
import pickle
import yaml
import argparse
import random
import json
import time
import pygame
import pandas as pd
import multiprocessing as mp
from evolution.map_elites.me_cell import MECell
from evolution.visualization.grid_visualizer import GridVisualizer
from functools import partial
from micro_rct.rct_env import RCTEnv
from evolution.chromosome import Chromosome
from shutil import copyfile
from colorama import Fore, Back, Style
# colorama stuff
from colorama import init as init_colorama
init_colorama(autoreset=True)
class MapElitesRunner:

    def __init__(self, settings_path):
        with open(settings_path) as s_file:
            settings = yaml.load(s_file, yaml.FullLoader)
        
        self.pop = []
        self.settings = settings
        self.map = {}

        os.makedirs(settings.get('evolution', {}).get('save_path'), exist_ok=True)
    
    def initialize(self):
        gen_id = 0
        if self.settings.get('evolution', {}).get('checkpoint', {}).get('initialize_enabled'):
            gen_id = int(self.initialize_from_save()) + 1
        else:
            pop = []
            for i in range(0, self.settings.get('evolution', {}).get('population_size')):
                c = Chromosome(self.settings)
                pop.append(c)
            self.pop = pop
        return gen_id

    def initialize_from_save(self):
        checkpoint_path = self.settings.get('evolution', {}).get('checkpoint', {}).get('elite_path')
        gen_id = os.path.basename(checkpoint_path)
        if 0:
            for elite in [elite for elite in os.listdir(checkpoint_path) if elite.endswith('.p')]:
                elite_path = os.path.join(checkpoint_path, elite)
                with open(elite_path, 'rb') as f:
                    chrome = pickle.load(f)
                    key = self.get_dimension_key(chrome.dimensions)
                    self.map[key] = MECell(chrome.dimensions, self.settings.get('evolution', {}).get('cell_pop_size'))
                    self.map[key].set_chromosome(chrome)
        else:
            with open(checkpoint_path, 'rb') as f:
                self.map = pickle.load(f)
            gen_id = gen_id.split('.')[0]
        # init pop from elites
        self.mutate_generation()
        return gen_id

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
                self.map[key] = MECell(chrome.dimensions, self.settings.get('evolution', {}).get('cell_pop_size'))
            self.map[key].set_chromosome(chrome)

    def eval_chromosome(self, index, child_conn=None):
        chrome = self.pop[index]
        # print('eval {}'.format(index))
        chrome.simulate(ticks=self.settings.get('evolution', {}).get('eval_ticks'))
        if child_conn:
            child_conn.send((chrome.fitness, chrome.dimensions))

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
        if 0:
            path = self.settings.get('evolution', {}).get('save_path')
            path = os.path.join(path, '{}'.format(gen_id))
            os.makedirs(path, exist_ok=True)
            for dimension, cell in self.map.items():
                save_path = os.path.join(path, '{}.p'.format(dimension))
                self.save_chromosome(cell.elite, save_path)
        else:
            path = self.settings.get('evolution', {}).get('save_path')
            path = os.path.join(path, '{}.p'.format(gen_id))
            with open(path, 'wb') as f:
                pickle.dump(self.map, f)


    def get_grid(self):
        cells = []
        for dimen, cell in self.map.items():
            elite = cell.elite
            rep = '{dimen_color}Dimensions: {reg_1}{:<38s} | {fit_color}Fitness: {reg_2}{:>5d} | {age_color}Age: {reg_3}{:>3d}'.format(
                dimen, elite.fitness, elite.age, dimen_color=Fore.GREEN, fit_color=Fore.BLUE, age_color=Fore.MAGENTA, reg_1=Fore.WHITE, reg_2=Fore.WHITE, reg_3=Fore.WHITE)
            cells.append(rep)
        return cells

    def join_procs(self, processes):
        proc_idxs = list(processes.keys())
        for i in proc_idxs:
            # retrieve fitness scores and terminate parallel processes
            p, parent_conn = processes.pop(i)
            signal = parent_conn.recv()
            self.pop[i].fitness = signal[0]
            self.pop[i].dimensions = signal[1]
            p.join()
            p.close()

    def mutate_generation(self):
        new_pop = []

        for i in range(0, self.settings.get('evolution', {}).get('population_size')):
            # take a random elite
            if random.random() <= self.settings.get('evolution', {}).get('mutation_prob'):
                # qualify for mutation
                # pick a random cell and its elite
                elite = random.choice(list(self.map.values())).get_chromosome(self.settings.get('evolution', {}).get('elite_prob'))
                child = elite.mutate()
                new_pop.append(child)

            # TODO change this to add a chromosome without mutation       
            else:
                elite = random.choice(list(self.map.values())).get_chromosome(
                    self.settings.get('evolution', {}).get('elite_prob')).clone()
                child = elite.clone(elite.dimensions.keys())
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
                if i % n_threads == 0:
                    self.join_procs(processes)
            self.join_procs(processes)

        else:
            for i in range(0, len(self.pop)):
                self.eval_chromosome(i)
        # map elite grid
        self.assign_chromosomes()
        # [print(x) for x in self.get_grid()]
        # save gen
        if id % self.settings.get('evolution', {}).get('checkpoint', {}).get('save_nth_epoch') == 0 or id == int(self.settings.get('evolution', {}).get('gen_count')) - 1:
            self.save_elites(gen_id=id)
            # save grid image
            df = self.convert_map_to_df()
            visualizer = GridVisualizer(df)
            write_path = path = self.settings.get(
                'evolution', {}).get('save_path')
            write_path = os.path.join(write_path, '{}_map.html'.format(id))
            # visualizer.visualize(x='happiness', y='ride_count', val='fitness', write_path=write_path)
            visualizer.visualize(x='shop_count', y='ride_count', val='fitness', write_path=write_path)
        # run mutation
        self.mutate_generation()

    def convert_map_to_df(self):
        df = pd.DataFrame()
        
        df = pd.DataFrame([[value for value in cell.elite.dimensions.values()] for cell in self.map.values()], columns=[
            dimen for dimen in random.choice(list(self.map.values())).elite.dimensions.keys()])
        fitness_df = pd.DataFrame([cell.elite.fitness for cell in self.map.values()], columns=['fitness'])
        age_df = pd.DataFrame([cell.elite.age for cell in self.map.values()], columns=['age'])
        df = df.join(fitness_df)
        df = df.join(age_df)
        # for dimen, cell in self.map.items():
        #     elite_df = pd.DataFrame([cell.elite.fitness], columns=[cell.elite])
        #     df = df.join(elite_df)
        return df

class MapElitesAnalysis:
    def __init__(self, settings_path):
        with open(settings_path) as s_file:
            self.settings = yaml.load(s_file, yaml.FullLoader)

    def render_elites(self, gen_id):
        filepath = self.settings.get('evolution', {}).get('save_path')
        if 0:
            gen_id = int(gen_id)
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
        else:
            filepath = os.path.join(filepath, '{}'.format(gen_id))
            os.makedirs(filepath.split('.')[0], exist_ok=True)
            with open(filepath, 'rb') as f:
                self.map = pickle.load(f)
                for dim, cell in self.map.items():
                    cell.elite.settings['general']['render'] = True
                    cell.elite.rct.render_gui = True
                    cell.elite.rct.rct_env.set_rendering(True)
                    cell.elite.rct.rct_env.resetSim()
                    cell.elite.rct.rct_env.render_map.render_park()
                    img = cell.elite.rct.rct_env.screen
                    img_name = '{}.png'.format(dim)
                    # with open(os.path.join(filepath, img_name), 'w+') as save_file:
                    pygame.image.save(img, os.path.join(filepath.split('.')[0], img_name))

def main(settings_path):
    with open(settings_path) as s_file:
        settings = yaml.load(s_file, yaml.FullLoader)
    if settings.get('evolution', {}).get('action') == 'evolve':
        start = time.time()
        runner = MapElitesRunner(settings_path)
        gen_id = runner.initialize()
        init_time = time.time() - start
        print('{}Time: {}{}'.format(Fore.MAGENTA, Fore.WHITE, init_time))
        # print(Fore.GREEN + '** POP BREAKDOWN **')
        # print('\n'.join(map(str, runner.get_statistics())))
        # print(runner.get_statistics())
        for i in range(gen_id, settings.get('evolution', {}).get('gen_count') + gen_id):
            start = time.time()
            runner.run_generation(i)
            end = time.time()
            if settings.get('evolution', {}).get('print_map'):
                print('\n'.join(map(str, runner.get_grid())))
            print('{}Time: {}{}'.format(Fore.MAGENTA, Fore.WHITE, (end-start)))

    else:
        analyzer = MapElitesAnalysis(settings_path)
        for generation in os.listdir(analyzer.settings.get('evolution', {}).get('save_path')):
            if generation.endswith('.p'):
                analyzer.render_elites(generation)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
