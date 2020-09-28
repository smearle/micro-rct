import copy
import random
import sys
import time
import argparse
import yaml

from tqdm import tqdm

from micro_rct.map_utility import placePath, placeRide
from micro_rct.park import Park
from micro_rct.path import PathFinder
from micro_rct.peeps_generator import generate
from micro_rct.rct_test_objects import object_list as ride_list
from micro_rct.rct_test_objects import symbol_list
from micro_rct.tilemap import Map
from utils.debug_utils import print_msg

def main(settings_path):
    with open(settings_path) as file:
        settings = yaml.load(file, yaml.FullLoader)
    env = RCTEnv(settings)

    for n_ticks in settings['experiments']['ticks']:
        run_experiment(env, n_ticks, settings)
        
def run_experiment(env, n_ticks, settings, n_trials=20):
    start_time = time.time()
    env.reset()

    for i in tqdm(range(n_trials)):
        log_name = 'output_logs/guests_{}_ticks_{}_trial_{}'.format(settings['environment']['n_guests'], n_ticks, i)
        orig_stdout = sys.stdout
        f = open(log_name, 'w')
        sys.stdout = f
        env.simulate(n_ticks)
        sys.stdout = orig_stdout
        f.close()
    print('Experiment log filename: {}\n Time elapsed: {}'.format(log_name, time.time() - start_time))


class RCTEnv():
    N_RIDES = len(ride_list)

    def __init__(self, settings):
        if settings['general']['render']:
            import pygame
            pygame.init()
            screen_width = 1000
            screen_height = 1000
            self.screen = pygame.display.set_mode((screen_width, screen_height))
        else:
            self.screen = None
        self.settings = settings
        self.render_map = None

    def reset(self):
        print_msg('resetting park', priority=2, verbose=self.settings['general']['verbose'])
        self.park = Park(self.settings)
        placePath(self.park, margin=3)

        for _ in range(self.settings['environment']['n_actions']):
            ride_i = random.randint(0, self.N_RIDES-1)
            placeRide(self.park, ride_i, verbose=self.settings['general']['verbose'])
        self.park.populate_path_net()
        path_finder = PathFinder(self.park.path_net)
        peeps = generate(
            self.settings['environment']['n_guests'], self.park, 0.2, 0.2, path_finder)

        for p in peeps:
            self.park.updateHuman(p)

        if not self.render_map:
            self.render_map = Map(self.park, render=self.settings['general']['render'], screen=self.screen)
        else:
            self.render_map.reset(self.park)

    def simulate(self, n_ticks=-1):
        frame = 0

        while frame < n_ticks or n_ticks == -1:
            self.park.update(frame)

            if self.settings['general']['render']:
                self.render_map.render_park()
            frame += 1





#def run_trial(n_ticks):
#    park = Park(MAP_HEIGHT, MAP_WIDTH)
#    #place the path
#    placePath(park, margin=3)
#    park.printPark()
#    #place the ride (park, ride object, marks)
#
#    for _ in range(10):
#        ride_i = random.randint(0, N_RIDES-1)
#        placeRide(park, ride_list[ride_i], str(symbol_list[ride_i]))
#    park.populate_path_net()
#    path_finder = PathFinder(park.path_net)
#    peeps = generate(N_GUESTS, 0.2, 0.2, path_finder)
#    park.printPark()
#    #place the guest
#
#    for p in peeps:
#        res = park.updateHuman(p)
#
#        for line in res:
#            print(line)
#    park.printPark()
#    #testing
#    frame = 0
#
#    if n_ticks == -1:
#        map = Map(park)
#        while True:
#            park.update(frame)
##           time.sleep(0.4)
#            map.render_park()
#            # NB: might overflow
#            frame += 1
#
#    map = Map(park)
#    for _ in range(n_ticks):
#        frame += 1
#        park.update(frame)
#        map.render_park()
#    del(park)
#    del(path_finder)
#    del(peeps)
#    return

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml', help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
