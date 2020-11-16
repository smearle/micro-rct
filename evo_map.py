import argparse
import copy
import os
import pickle
import random
import time
from multiprocessing import Pipe, Process
from shutil import copyfile

import numpy as np

from micro_rct.gym_envs.rct_env import RCT

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
        evolver = LambdaMuEvolver(save_path,
                                  n_pop=args.n_pop,
                                  lam=args.lam,
                                  mu=args.mu)

    if args.inference:
        evolver.infer(200)
    else:
        evolver.evolve()


def simulate_game(game, n_ticks, conn=None):
    game.resetSim()
    scores = game.simulate(n_ticks)
    score = np.mean(scores)
    255 - score  # unhappiness is good

    if conn:
        conn.send(score)

    return score


class LambdaMuEvolver():
    def __init__(
            self,
            save_path,
            n_pop=12,
            lam=1 / 3,
            mu=1 / 3,
    ):
        self.lam = lam
        self.mu = mu
        self.population_size = n_pop
        self.n_epochs = 11000
        self.n_sim_ticks = 100
        self.n_init_builds = 3
        self.max_mutate_builds = self.n_init_builds
        self.save_path = save_path
        self.n_epoch = 0
        self.population = {}  # hash: (game, score, age)
        self.score_var = {}
        self.gens_alive = {}
        self.mature_age = 3

    def evolve(self):

        if not self.population:
            for i in range(self.population_size):
                game = RCT(settings_path='configs/settings.yml', rank=i)
                game.reset()
                game = self.genRandMap(game)
                self.population[i] = (game, None, 0)
                self.score_var[i] = None, []
                self.gens_alive[i] = 0

        while self.n_epoch < self.n_epochs:
            start_time = time.time()
            self.evolve_generation()
            time_elapsed = time.time() - start_time
            hours, rem = divmod(time_elapsed, 3600)
            minutes, seconds = divmod(rem, 60)
            print("time elapsed: {:0>2}:{:0>2}:{:05.2f}".format(
                int(hours), int(minutes), seconds))

    def infer(self, n_ticks):
        while True:
            for g_hash in self.population:
                game = self.population[g_hash][0]
                game.resetSim()
                score = simulate_game(game, n_ticks)
                print('game {} score: {}'.format(g_hash, score))

    def join_procs(self, processes):
        pop_hashes = []

        for g_hash, (p, parent_conn, child_conn) in processes.items():
            score_t = parent_conn.recv()
            p.join()
            game, score, age = self.population[g_hash]

            if score is not None:
                score = (score * age) / (age + 1) + score_t / (age + 1)
            else:
                score = score_t
            self.population[g_hash] = (game, score, age + 1)
            pop_hashes.append(g_hash)
            score_var, score_hist = self.score_var[g_hash]

            if len(score_hist) == 10:
                score_hist.pop(0)
            score_hist.append(score)

            if len(score_hist) > 1:
                score_var = max(score_hist) - min(score_hist)
            self.score_var[g_hash] = score_var, score_hist

        for h in pop_hashes:
            processes.pop(h)

    def evolve_generation(self):
        print('epoch {}'.format(self.n_epoch))
        population = self.population
        n_cull = int(self.population_size * self.mu)
        n_parents = int(self.population_size * self.lam)
        dead_hashes = []
        processes = {}

        n_proc = 0
        var_thresh = 1

        for g_hash, (game, score, age) in population.items():
            score_var, score_hist = self.score_var[g_hash]
            self.gens_alive[g_hash] = self.gens_alive[g_hash] + 1

            if age > self.mature_age * 2 and len(
                    score_hist) >= 10 and score_var < var_thresh:

                if random.random() > (score_var / var_thresh):
                    continue

            if not game.render_gui:
                parent_conn, child_conn = Pipe()
                p = Process(target=simulate_game,
                            args=(
                                game,
                                self.n_sim_ticks,
                                child_conn,
                            ))
                p.start()
                processes[g_hash] = p, parent_conn, child_conn
                n_proc += 1

            else:
                score_t = simulate_game(game, self.n_sim_ticks)
                if age:
                    score = (score * age) / (age + 1) + score_t / (age + 1)
                else:
                    score_t = score
                population[g_hash] = (game, score, age + 1)

        self.join_procs(processes)

        ranked_pop = [(g_hash, game, score, age)
             for g_hash, (game, score, age) in population.items()]
        ranked_pop = sorted(ranked_pop, key=lambda tpl: tpl[2])
        print('ranked pop: (id, score, n_sims, n_gens, score_var)')

        for g_hash, game, score, age in ranked_pop:
            n_gens = self.gens_alive[g_hash]
            score_var = self.score_var[g_hash][0]
            print('{}, {:2f}, {}, {}, {}'.format(g_hash, score, age, n_gens,
                                                 score_var))

        for j in range(n_cull):
            dead_hash = ranked_pop[j][0]

            if self.population[dead_hash][2] > self.mature_age:
                dead_hashes.append(dead_hash)

        par_hashes = []

        for i in range(n_parents):
            par_hash, _, _, age = ranked_pop[-(i + 1)]

            if age > self.mature_age:
                par_hashes.append(par_hash)

        # for all we have called, add new mutated individual
        j = 0

        if par_hashes:
            while dead_hashes:
                n_parent = j % len(par_hashes)
                par_hash = par_hashes[n_parent]
                parent = population[par_hash]
                par_game = parent[0]  # get game from (game, score, age) tuple
                child_hash = dead_hashes.pop()
                population.pop(child_hash)
                self.score_var.pop(child_hash)
                child_game = self.mutate(par_game, child_hash)
                population[child_hash] = (child_game, None, 0)
                self.score_var[child_hash] = None, []
                self.gens_alive[child_hash] = 0
                j += 1

        if self.n_epoch % 10 == 0:
            self.save()

        self.n_epoch += 1

    def save(self):
        save_file = open(self.save_path, 'wb')
        # destroy a bunch of references to GUI since we can't render this

        for game, _, _ in self.population.values():
            game.rct_env.screen = None
            game.rct_env.render_map = None
        from os import environ
        environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        import pygame
        pygame.quit()
        copyfile(self.save_path, self.save_path + '.bkp')
        pickle.dump(self, save_file)

    def genRandMap(self, game):
        #       game.place_ride_tile(7, 7, 3, 0)
        #       game.place_ride_tile(8, 8, 3, 0)
        #       game.place_ride_tile(10, 10, 10, 0)

        for i in range(self.n_init_builds):
            # for i in range(1000):
            game.act(game.action_space.sample())

        for i in range(random.randint(0, 3)):
            game.rand_connect()

        return game

    def mutate(self, par_game, child_hash):
        child = par_game.clone(settings_path='configs/settings.yml',
                               rank=child_hash)

        child.resetSim()

        n_builds = random.randint(1, self.max_mutate_builds)

        for i in range(n_builds):
            action = child.action_space.sample()

            if action['act'] == RCT.BUILDS.PATH:
                action['act'] = RCT.BUILDS.DEMOLISH
            child.act(child.action_space.sample())

    # for i in range(random.randint(0, 1)):
    #    child.rand_connect()
        child.delete_islands()

        return child


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
                        default=1 / 3,
                        help='number of reproducers each epoch')
    parser.add_argument(
        '--mu',
        type=float,
        default=1 / 3,
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
