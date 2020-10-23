import copy
import random
import sys
import time
import argparse
import yaml

from tqdm import tqdm

from micro_rct.map_utility import placePath, placeRide
from micro_rct.park import Park
from micro_rct.pathfinding import PathFinder
from micro_rct.peeps_generator import generate
from micro_rct.rct_test_objects import object_list as ride_list
from micro_rct.rct_test_objects import symbol_list
from micro_rct.tilemap import Map
from micro_rct.utils.debug_utils import print_msg


class RCTEvolution:
    def __init__(self, settings, population_size=50):
        self.settings = settings
        self.N_RIDES = len(ride_list)  # number of rides available

        # initialize park, path
        self.park = Park(self.settings)
        placePath(self.park, margin=3)

        # initialize the initial (random) population of rides --- why are there so many initials in this sentence ffs
        for _ in range(population_size - 1):
            ride_i = random.randint(0, self.N_RIDES - 1)
            placeRide(self.park, ride_i, verbose=False)

    def simulate_park(self, n_ticks=100):
        print("simulation")
        frame = 0
        while frame < n_ticks or n_ticks == -1:
            # print("frame = ", frame)
            self.park.update(frame)
            frame += 1

        return self.park.returnScore()

    def reset(self):
        # reinitialize the peeps and path for each park
        self.park.populate_path_net()
        path_finder = PathFinder(self.park.path_net)

        # generate peeps
        park_peeps = generate(
            self.settings['environment']['n_guests'], self.park, 0.2, 0.2, path_finder)
        for p in park_peeps:
            self.park.updateHuman(p)

    def mutate_rides(self):
        print("mutation")
        add_prob = 0.3
        delete_prob = 0.1
        move_prob = 0.4

        # iterate through list of rides and mutate by either deleting or moving the ride
        # TODO: Deleting and Moving rides

        # after (potentially) mutating every object, separately check mutation probability to add
        if random.uniform(0, 1) <= add_prob:
            print("mutating - adding ride")
            ride_i = random.randint(0, self.N_RIDES - 1)
            placeRide(self.park, ride_i, verbose=True)

    def evolutionary_search(self, n_ticks=100):
        # initialize number of generations, mutation probabilities
        generations = 5

        # initialize peeps
        print("resetting peeps")
        self.reset()

        # evaluate initial park
        bestPark = self.park  # set best fit park as the initial park
        bestFitness = self.simulate_park(n_ticks)

        for _ in range(generations):
            print("current best fitness: ", bestFitness)

            # create child node of existing park
            childPark = copy.deepcopy(self)

            # mutate the child parks
            childPark.mutate_rides()

            # reset peeps each generation to reset needs
            childPark.reset()

            # evaluate the child
            childScore = childPark.simulate_park(n_ticks)

            # evaluate park
            print("current best:", bestFitness, "new fitness: ", childScore)
            if childScore > bestFitness:
                print("replacing with new child")
                bestPark = childPark  # set best fit park as the initial park
                bestFitness = childScore

        # TODO: save best house and generation stats to log

    def run_experiment(self, n_ticks, settings, n_trials=20):
        start_time = time.time()
        # self.evolutionary_search(n_ticks)

        for i in tqdm(range(n_trials)):
            log_name = 'output_logs/evolutionary_search_{}_ticks_{}_trial_{}'.format(
                settings['environment']['n_guests'], n_ticks, i)
            orig_stdout = sys.stdout
            f = open(log_name, 'w')
            sys.stdout = f
            self.evolutionary_search(n_ticks)
            sys.stdout = orig_stdout
            f.close()

        print('Experiment log filename: {}\n Time elapsed: {}'.format(log_name, time.time() - start_time))


def main(settings_path):
    with open(settings_path) as file:
        settings = yaml.load(file, yaml.FullLoader)

    env = RCTEvolution(settings, population_size=50)

    for n_ticks in settings['experiments']['ticks']:
        print("n_ticks = ", n_ticks)
        env.run_experiment(n_ticks, settings)

    # env.run_experiment(n_ticks=500, settings=settings)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
