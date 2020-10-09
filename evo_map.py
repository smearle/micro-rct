import copy
import argparse
import os
import numpy as np
import random
import pickle
from shutil import copyfile

from gym_micro_rct.envs.rct_env import RCT

# FIXME: If we reload a file with a different rendering option, pickled games will still
# have the old option (newly cloned ones will not).

def main():
    game = RCT(settings_path='configs/settings.yml')
    game.reset()

    while True:
        game.rct_env.simulate(100)
        game.resetSim()


def evolve(experiment_name, load):
    save_path = os.path.join('experiments', experiment_name)
    if load:
        save_file = open(save_path, 'rb')
        evolver = pickle.load(save_file)
    elif os.path.exists(save_path):
        raise Exception('experiment exists -- not loading or overwriting')
    else:
        evolver = LambdaMuEvolver(save_path)
    evolver.main()


class LambdaMuEvolver():
    def __init__(self, save_path):
        self.lam = 0.2
        self.mu = 0.2
        self.population_size = 10
        self.n_epochs = 10000
        self.n_sim_ticks = 200
        self.n_init_builds = 30
        self.max_mutate_builds = 10
        self.save_path = save_path
        self.n_epoch = 0
        self.population = {}  # hash: (game, score, age)

    def main(self):
        
        if not self.population:
            for i in range(self.population_size):
                game = RCT(settings_path='configs/settings.yml', rank=i)
                game.reset()
                game = self.genRandMap(game)
                self.population[i] = (game, None, 0)

        while self.n_epoch < self.n_epochs:
            self.evolve_generation(self.n_epoch)


    def evolve_generation(self, i):
        print('epoch {}'.format(i))
        population = self.population
        n_cull = int(self.population_size * self.mu)
        n_parents = int(self.population_size * self.lam)
        dead_hashes = []

        for g_hash, (game, score, age) in population.items():
            game.resetSim()
            scores = game.simulate(self.n_sim_ticks)
            score = np.mean(scores)
            score = 255 - score # unhappiness is good
            population[g_hash] = (game, score, age + 1)
        ranked_pop = sorted(
            [(g_hash, game, score, age)
             for g_hash, (game, score, age) in population.items()],
            key=lambda tpl: tpl[2])
        print('ranked pop: (score, age)')
        for g_hash, game, score, age in ranked_pop:
            print('{:2f}, {}'.format(score, age))

        for j in range(n_cull):
            dead_hash = ranked_pop[j][0]
            dead_hashes.append(dead_hash)

        j = 0

        while j < n_cull:
            n_parent = j % n_parents
            par_hash = ranked_pop[-(n_parent + 1)][0]
            parent = population[par_hash]
            par_game = parent[0]
            g_hash = dead_hashes.pop()
            population.pop(g_hash)
            child_game = self.mutate(par_game, g_hash)
            population[g_hash] = (child_game, None, 0)
            j += 1
        save_file = open(self.save_path, 'wb')
        # destroy a bunch of references to GUI since we can't render this
        for game, _, _ in self.population.values():
            game.rct_env.screen = None
            game.rct_env.render_map = None
        import pygame
        pygame.quit()
        copyfile(self.save_path, self.save_path + '.bkp')
        pickle.dump(self, save_file)
        self.n_epoch += 1


    def genRandMap(self, game):
        for i in range(self.n_init_builds):
            game.act(game.action_space.sample())
        game.render()

        return game

    def mutate(self, par_game, g_hash):
        child = par_game.clone(settings_path='configs/settings.yml', rank=g_hash)

        child.resetSim()
        for i in range(random.randint(1, self.max_mutate_builds)):
            child.act(child.action_space.sample())

        return child

    def save(self):
        pass

    def load(self):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--experiment-name',
                        default='evo_test_0',
                        help='name of the experiment')
    parser.add_argument('--load',
                        default=False,
                        help='whether or not to load a previous experiment')
    args = parser.parse_args()
    experiment_name = args.experiment_name
    load = args.load
    # main()
    evolve(experiment_name, load)
