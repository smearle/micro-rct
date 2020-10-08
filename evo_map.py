import copy
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
        self.n_epochs = 10000
        self.population_size = 5
        self.n_sim_ticks = 100
        self.n_init_builds = 100

    def main(self):
        population = {}  # hash: (game, score)

        for i in range(self.population_size):
            game = RCT(settings_path='configs/settings.yml')
            game.reset()
            game = self.genRandMap(game)
            population[i] = (game, None)

        for i in range(self.n_epochs):
            print('epoch {}'.format(i))
            n_cull = int(self.population_size * self.mu)
            n_parents = int(self.population_size * self.lam)
            dead_hashes = []

            for g_hash, game_score in population.items():
                game = game_score[0]
                game.resetSim()
                game.simulate(self.n_sim_ticks)
                population[g_hash] = (game, game.rct_env.park.score)
            ranked_pop = sorted(
                [(g_hash, game_score)
                 for g_hash, game_score in population.items()],
                key=lambda hash_game_score: hash_game_score[1][1])
            print('ranked pop: ', ranked_pop)

            for j in range(n_cull):
                dead_hash = ranked_pop[-(j + 1)][0]
                population.pop(dead_hash)
                dead_hashes.append(dead_hash)

            j = 0

            while j < n_cull:
                n_parent = j % n_parents
                par_hash = ranked_pop[n_parent][0]
                parent = population[par_hash]
                par_game = parent[0]
                child_game = self.mutate(par_game)
                g_hash = dead_hashes.pop()
                population[g_hash] = (child_game, None)
                j += 1

    def genRandMap(self, game):
        for i in range(self.n_init_builds):
            game.act(game.action_space.sample())
        game.render()

        return game

    def mutate(self, par_game):
        child = par_game.clone(settings_path='configs/settings.yml')

        for i in range(random.randint(1, 30)):
            child.act(child.action_space.sample())
       #child.resetSim()

        return child

    def save(self):
        pass

    def load(self):
        pass


if __name__ == '__main__':
    # main()
    evolve()
