import argparse
from .peep import Peep
import copy
import os
import random
import sys
import time

import yaml
from tqdm import tqdm

from .map_utility import placePath, placeRide, place_path_tile
from .park import Park
from .path import Path
from .pathfinding import PathFinder
from .peeps_generator import generate
from .rct_test_objects import object_list as ride_list
from .rct_test_objects import symbol_list
from .tilemap import Map
from .utils.debug_utils import print_msg


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
        log_name = 'output_logs/guests_{}_ticks_{}_trial_{}'.format(
            settings['environment']['n_guests'], n_ticks, i)
        orig_stdout = sys.stdout
        f = open(log_name, 'w')
        sys.stdout = f
        env.simulate(n_ticks)
        sys.stdout = orig_stdout
        f.close()
    print('Experiment log filename: {}\n Time elapsed: {}'.format(
        log_name,
        time.time() - start_time))


class RCTEnv():
    N_RIDES = len(ride_list)

    def __init__(self, settings, park=None):

        self.settings = settings
        self.set_rendering(settings['general']['render'])
        self.render_map = None
        if park == None:
            self.park = Park(self.settings)
        else:
            self.park = park
            self.resetSim()

    def set_rendering(self, val):
        if val:
            self.settings['general']['render'] = val
            from os import environ
            environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
            import pygame
            pygame.init()
            screen_width = self.settings.get(
                'general', {}).get('render_screen_width')
            screen_height = self.settings.get(
                'general', {}).get('render_screen_height')
            self.screen = pygame.display.set_mode(
                (screen_width, screen_height))
            self.screen_width, self.screen_height = screen_width, screen_height
        else:
            self.screen = None

    def reset(self):
        print_msg('resetting park',
                  priority=2,
                  verbose=self.settings['general']['verbose'])
        self.park = Park(self.settings)
        placePath(self.park, margin=3)

#       self.park.populate_path_net()
        path_finder = PathFinder(self.park.path_net)
        self.path_finder = path_finder
        peeps = generate(self.settings['environment']['n_guests'], self.park,
                         0.2, 0.2, path_finder)
        for peep in peeps:
            self.park.map[Map.PEEP, peep.position[0], peep.position[1]] += 1
        # FIXME: hack
        self.park.peeps_by_pos[Peep.ORIGIN] = peep
        self.park.peepsList = peeps

#       if not self.render_map:
#          #print('in rct env, initializing render map')
        self.render_map = Map(self.park,
                                  render=self.settings['general']['render'],
                                  screen=self.screen)
#       else:
#          #print('in rct env, not initializing render map')
#           self.render_map.reset(self.park)


    def resetSim(self):
        ''' Put the peeps back in place.'''
        for peep in self.park.peepsList:
            self.park.map[Map.PEEP, peep.position[0], peep.position[1]] = -1
        for (x, y) in self.park.path_net:
            self.park.map[Map.PATH, x, y] = Path.PATH
       #for pos, ride in self.park.rides_by_pos.items():
       #    self.park.map[Map.RIDE, pos[0], pos[1]] = ride.ride_i
        self.park.vomit_paths = {}
#       self.park.populate_path_net()
        self.path_finder = PathFinder(self.park.path_net)
        peeps = generate(self.settings['environment']['n_guests'], self.park,
                         0.2, 0.2, self.path_finder)
        self.park.peepsList = peeps

        for p in peeps:
            self.park.updateHuman(p)

        if not self.screen and self.settings['general']['render']:
            from os import environ
            environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
            import pygame
            pygame.init()
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.render_map = Map(self.park,
                              render=self.settings['general']['render'],
                              screen=self.screen)
       #self.render_map.reset(self.park)

       # Don't reset park money, or we will effectively allow for cost-free mutation during MAP-Elites
       #self.park.money = Park.INIT_MONEY

    def simulate(self, n_ticks=-1):
        if n_ticks != -1:
            scores = []
       #for _ in range(self.settings['environment']['n_actions']):
       #    ride_i = random.randint(0, self.N_RIDES - 1)
       #    placeRide(self.park,
       #              ride_i,
       #              verbose=self.settings['general']['verbose'])
        frame = 0

        while frame < n_ticks or n_ticks == -1:
            self.park.update(frame)
            if n_ticks != -1:
                scores.append(self.park.score)

            if self.settings['general']['render']:
                self.render_map.render_park()
                self.park.printPark()
            frame += 1
        return scores


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path',
                        '-sp',
                        default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
