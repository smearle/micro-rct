import copy
import numpy as np
import random

from gym_micro_rct.envs.rct_env import RCT


def main():
    game = RCT(settings_path='configs/settings.yml')
    game.reset()

    while True:
        game.rct_env.simulate(100)
        game.resetSim()


def evolve():
    evolver = LambdaMuEvolver()
    evolver.main()


class LambdaMuEvolver():
    def __init__(self):
        self.lam = 0.2
        self.mu = 0.2
        self.population_size = 10
        self.n_epochs = 10000
        self.n_sim_ticks = 500
        self.n_init_builds = 1

    def main(self):
        population = {}  # hash: (game, score, age)

        for i in range(self.population_size):
            print(i)
            game = RCT(settings_path='configs/settings.yml', rank=i)
            game.reset()
            game = self.genRandMap(game)
            population[i] = (game, None, 0)

        for i in range(self.n_epochs):
            print('epoch {}'.format(i))
            n_cull = int(self.population_size * self.mu)
            n_parents = int(self.population_size * self.lam)
            dead_hashes = []

            for g_hash, (game, score, age) in population.items():
                game.resetSim()
                scores = game.simulate(self.n_sim_ticks)
                score = np.mean(scores)
                score = 255 - score # vomit is good
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

    def genRandMap(self, game):
        for i in range(self.n_init_builds):
            game.act(game.action_space.sample())
        game.render()

        return game

    def mutate(self, par_game, g_hash):
        child = par_game.clone(settings_path='configs/settings.yml', rank=g_hash)

        child.resetSim()
        for i in range(random.randint(1, 3)):
            child.act(child.action_space.sample())

        return child

    def save(self):
        pass

    def load(self):
        pass


if __name__ == '__main__':
    # main()
    evolve()
