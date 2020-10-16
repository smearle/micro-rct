import argparse
import copy
import os
import pickle
import random
from multiprocessing import Process, Pipe
from shutil import copyfile

import numpy as np

from gym_micro_rct.envs.rct_env import RCT

# FIXME: If we reload a file with a different rendering option, pickled games will still
# have the old option (newly cloned ones will not).

def main():
    game = RCT(settings_path='configs/settings.yml')
    game.reset()

    while True:
        game.rct_env.simulate(100)
        game.resetSim()


def evolve(experiment_name, load, args):
    save_path = os.path.join('experiments', experiment_name)

    if load:
        try:
            save_file = open(save_path, 'rb')
            evolver = pickle.load(save_file)
        except Exception:
            print('no save file to load')
    elif os.path.exists(save_path):
        raise Exception('experiment exists -- not loading or overwriting')
    else:
        evolver = LambdaMuEvolver(save_path, n_pop=args.n_pop, lam=args.lam, mu=args.mu)
    if args.inference:
        evolver.infer(200)
    else:
        evolver.main()

def simulate_game(game, n_ticks, conn=None):
    game.resetSim()
    scores = game.simulate(n_ticks)
    score = np.mean(scores)
    255 - score # unhappiness is good
    if conn:
        conn.send(score)
    return score



class LambdaMuEvolver():
    def __init__(self, 
            save_path, 
            n_pop = 12, 
            lam = 1/3, 
            mu = 1/3,
            ):
        self.lam = lam
        self.mu = mu
        self.population_size = n_pop
        self.n_epochs = 11000
        self.n_sim_ticks = 1000
        self.n_init_builds = 3
        self.max_mutate_builds = self.n_init_builds
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

    def infer(self, n_ticks):
        while True:
            for g_hash in self.population:
                game = self.population[g_hash][0]
                game.resetSim()
                score = simulate_game(game, n_ticks)
                print('game {} score: {}'.format(g_hash, score))


    def evolve_generation(self, i):
        print('epoch {}'.format(i))
        population = self.population
        n_cull = int(self.population_size * self.mu)
        n_parents = int(self.population_size * self.lam)
        dead_hashes = []
        processes = {}

        for g_hash, (game, score, age) in population.items():
            if not game.render_gui:
                parent_conn, child_conn = Pipe()
                p = Process(target=simulate_game, args=(game, self.n_sim_ticks, child_conn,))
                p.start()
                processes[g_hash] = p, parent_conn, child_conn
            else:
                score = simulate_game(game, self.n_sim_ticks)
                population[g_hash] = (game, score, age + 1)
        for g_hash, (p, parent_conn, child_conn) in processes.items():
            score = parent_conn.recv()
            p.join()
            game, _, age = population[g_hash]
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
#       game.place_ride_tile(7, 7, 3, 0)
#       game.place_ride_tile(8, 8, 3, 0)
#       game.place_ride_tile(10, 10, 10, 0)
        for i in range(self.n_init_builds):
       #for i in range(1000):
            game.act(game.action_space.sample())
        for i in range(random.randint(0, 3)):
            game.rand_connect()

        return game

    def mutate(self, par_game, g_hash):
        child = par_game.clone(settings_path='configs/settings.yml', rank=g_hash)

        child.resetSim()

        n_builds = random.randint(1, self.max_mutate_builds)
        for i in range(n_builds):
            action = child.action_space.sample()
            if action['act'] == RCT.BUILDS.PATH:
                action['act'] = RCT.BUILDS.DEMOLISH
            child.act(child.action_space.sample())
       #for i in range(random.randint(0, 1)):
       #    child.rand_connect()
        child.delete_islands()

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
                        action='store_true',
                        help='whether or not to load a previous experiment')
    parser.add_argument('--n-pop',
                        type=int,
                        default=12,
                        help='population size')
    parser.add_argument('--lam',
                        type=float,
                        default=1/3,
                        help='number of reproducers each epoch')
    parser.add_argument('--mu',
                        type=float,
                        default=1/3,
                        help='number of individuals to cull and replace each epoch')
    parser.add_argument('--inference',
                        default=False,
                        action='store_true',
                        help='watch simulations on evolved maps')
    args = parser.parse_args()
    experiment_name = args.experiment_name
    load = args.load
    # main()
    evolve(experiment_name, load, args)
