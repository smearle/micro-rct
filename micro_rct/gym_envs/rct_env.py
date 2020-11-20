import copy
import os
import random
import sys
import time

import gym
import numpy as np
#import torch
import yaml
from gym import core
from micro_rct import map_utility
from micro_rct.map_utility import placePath, placeRide
from micro_rct.park import Park
from micro_rct.pathfinding import PathFinder
from micro_rct.peep import Peep
from micro_rct.peeps_generator import generate
from micro_rct.rct_env import RCTEnv
from micro_rct.rct_test_objects import object_list as ride_list
from micro_rct.rct_test_objects import symbol_list
from micro_rct.tilemap import Map


def main(settings):

    env = RCT(settings_path=settings, rank=1)

    while True:
        env.reset()

        for i in range(100):
            env.act(env.action_space.sample())
            env.delete_islands()

            if env.render_gui:
                env.render()

def parse_kwargs(kwargs):
        ''' If we are missing a settings object, use kwargs to generate one.'''
        settings = {
                'general': {
                    'render': kwargs['render'],
                    'verbose': False,
                    'render_screen_width': 500,
                    'render_screen_height': 500,
                    },
                'environment': {
                    'n_guests': 10,
                    'map_width': kwargs.get('map_width', 16),
                    'map_height': kwargs.get('map_width', 16),
                    },
                'experiments': {}
                }
        for kwarg in kwargs:
            for s_type in settings:
                if kwarg in settings[s_type]:
                    settings[s_type][kwarg] = kwargs.get(kwarg)
        return settings


class RCT(core.Env):
    class BUILDS:
        RIDE = 0,
        PATH = len(ride_list)
        DEMOLISH = PATH + 1
    RENDER_RANK = 0
    ACTION_SPACE = 1
    N_SIM_STEP = 100
    def __init__(self, **kwargs):
        self.rank = kwargs.get('rank', 0)
        settings = kwargs.get('settings', None)

        if settings:
            self.render_gui = settings['general']['render']

        else:
            self.render_gui = kwargs['render'] = kwargs.get('render_gui', True) and self.rank == RCT.RENDER_RANK
            settings = parse_kwargs(kwargs)
        self.rct_env = RCTEnv(settings)
        core.Env.__init__(self)
        self.max_step = kwargs.get('max_step', 200)
        self.MAP_WIDTH = settings['environment']['map_width']
        self.MAP_HEIGHT = settings['environment']['map_height']
        # N.B.: the environment will use different data structures depending on whether or not paths are fixed, so we
        # cannot change this variable mid-game.
        self.FIXED_PATH = settings.get('environment', {}).get('fixed_path', True)
        self.ride_range = settings.get('environment', {}).get('ride_range', (0, 1))

        if self.render_gui:
            print('render rank', self.render_gui, self.rank)
            pass
        self.width = self.map_width = self.MAP_WIDTH
        self.n_step = 0
        self.metric_trgs = {
            'happiness': 0,
        }
        self.param_bounds = {
            'happiness': (0, 255),
        }
        self.init_metrics = {
            'happiness': 128,
        }
        self.weights = {
            'happiness': 1,
        }
        self.metrics = copy.deepcopy(self.init_metrics)
        N_OBS_CHAN = len(ride_list) + 3  # path and peeps, lack of ride
        obs_shape = (N_OBS_CHAN, self.MAP_WIDTH, self.MAP_HEIGHT)
        low = np.zeros(obs_shape)
        high = np.ones(obs_shape)
        self.observation_space = gym.spaces.Box(low, high)
        act_shape = (2)
        low = np.zeros(act_shape)
        high = np.zeros(act_shape)
        high[0] = self.MAP_WIDTH
        high[1] = self.MAP_HEIGHT
        self.N_ACT_CHAN = len(ride_list) + 2  # build a ride, place path, or demolish
        self.action_space = gym.spaces.MultiDiscrete(
                (self.MAP_WIDTH, self.MAP_HEIGHT, self.N_ACT_CHAN, 4)
                )

    def configure(self):
        pass

    def place_rand_path_net(self):
        pass

    def rand_connect(self):
        ''' Deprecated. Connects two random path tiles. Redundant if we're always either using a fixed path or rides
        with automatically connected paths.'''
        waypoints = [ride.entrance for ride in self.rct_env.park.rides_by_pos.values()] + [Peep.ORIGIN]
        try:
            src = waypoints.pop(random.randint(0, len(waypoints)))
            trg = waypoints.pop(random.randint(0, len(waypoints)))
        except IndexError:
            print('not enough potential waypoints to create connecting path')
            return
        path_seq = self.connect_with_path(src, trg)

        for (x, y) in path_seq:
            self.place_path_tile(x, y)
            self.render()

    def delete_islands(self):
        rides_by_pos = self.rct_env.park.rides_by_pos
        path_net = self.rct_env.park.path_net
        arr = self.rct_env.park.map
        xs, ys = np.where(self.rct_env.park.map[Map.PEEP] > -1)
        checking = list(zip(xs, ys))
        checked = []

        while checking:
            curr = checking.pop(0)
            curr_path  = self.rct_env.park.path_net[curr]
            # cannot flow through entrances
            if curr_path.is_entrance:
                checked.append((curr))
                continue

            for delta in [(0,1),(1,0),(-1,0),(0,-1)]:
                x, y = curr[0] + delta[0], curr[1] + delta[1]

                if (x, y) not in checking and (x, y) not in checked and \
                    0 <= x < arr.shape[1] and 0 <= y < arr.shape[2] and \
                    arr[Map.PATH, x, y] != -1:
                    checking.append((x, y))
            checked.append((curr))

        path_idxs = list(path_net.keys())
        for (i, j) in path_idxs:
            if (i, j) not in checked:
                assert self.demolish_tile(i, j)

    def connect_with_path(self, src, trg):
        path_seq = self.rct_env.path_finder.find_map(self.rct_env.park.map, src, trg)

        return path_seq

    def place_path_tile(self, x, y, type_i=0):
        if type_i % 2 == 0:
            map_utility.place_path_tile(self.rct_env.park, x, y)
        self.rct_env.park.populate_path_net()

    def place_ride_tile(self, x, y, ride_i, rotation):
        ride = map_utility.place_ride_tile(self.rct_env.park, x, y, ride_i,
                                    rotation)
        if not ride:
            return
        path_seq = self.connect_with_path(ride.entrance, Peep.ORIGIN)

        for pos in path_seq:
            self.place_path_tile(*pos)

    def demolish_tile(self, x, y):
        return map_utility.try_demolish_tile(self.rct_env.park, x, y)

    def update_metrics(self):
        self.metrics = {
            'happiness': self.rct_env.park.avg_peep_happiness,
        }

    def rand_act(self):
        return self.act(self.action_space.sample())

    def reset(self):
        self.rct_env.reset()
        rides_count = random.randint(self.ride_range[0], self.ride_range[1])
        for i in range(0, rides_count):
            self.act(self.action_space.sample())
        self.n_step = 0
        obs = self.get_observation()

        return obs

    def get_observation(self):
        obs = np.zeros(self.observation_space.shape)
        obs[:2, :, :] = np.clip(self.rct_env.park.map[:2, :, :] + 1, 0, 1)
        ride_obs = self.rct_env.park.map[Map.RIDE] + 1
        ride_obs = ride_obs.reshape((1, *ride_obs.shape))
        ride_obs_onehot = np.zeros(
            (len(ride_list) + 1, self.MAP_WIDTH, self.MAP_HEIGHT))
        xs, ys = np.indices(ride_obs.shape[1:])
        ride_obs_onehot[ride_obs, xs, ys] = 1
        obs[2:, :, :] = ride_obs_onehot

        return obs

    def act(self, action):
        # FIXME: hack to support gym-city implementation
        if len(action.shape) > 1:
            assert action.shape[1] == 1
            action = action[:, 0]
        if RCT.ACTION_SPACE == 0:
            x, y, build, rotation = self.ravel_action(action)
        elif RCT.ACTION_SPACE == 1:
            x = action[0]
            y = action[1]
            build = action[2]
            rotation = action[3]

        if self.FIXED_PATH:
            if build < len(ride_list) or len(self.rct_env.park.rides_by_pos) == 0:
                build = build % len(ride_list)
                self.place_ride_on_fixed_path(build)
            else:
                self.delete_rand_ride()
        else:
            if build < len(ride_list):
                self.place_ride_tile(x, y, build, rotation)
            elif build < len(ride_list) + 1:
                self.place_path_tile(x, y)
            else:
                self.demolish_tile(x, y)
        self.delete_islands()

    def delete_rand_ride(self):
        x, y = random.choice(list(self.rct_env.park.rides_by_pos.keys()))
        return self.demolish_tile(x, y)

    def place_ride_on_fixed_path(self, ride_i):
        return map_utility.placeRide(self.rct_env.park, ride_i)

    def step_sim(self):
        self.rct_env.park.update(self.n_step)
        self.update_metrics()

    def step(self, action):
        self.act(action)
        done = self.n_step >= self.max_step
        reward = 0
        if done:
            self.rct_env.park.populate_path_net()
            for _ in range(RCT.N_SIM_STEP):
                self.step_sim()
                reward += self.rct_env.park.income
                self.render()
        obs = self.get_observation()
        reward = reward / (RCT.N_SIM_STEP)
        info = {}

        if self.render_gui:
            self.render()
        self.n_step += 1

        return obs, reward, done, info

    def render(self, mode='human', close=False):
        if self.render_gui:
            img = self.rct_env.render_map.render_park()
            self.rct_env.park.printPark()

    def simulate(self, n_ticks=-1):
        scores = []

        for i in range(n_ticks):
            self.step_sim()
            self.render()
            self.n_step += 1
            scores.append(self.metrics['happiness'])

        return np.mean(scores)

    def resetSim(self):
        self.rct_env.resetSim()
        self.render()

    def clone(self, rank=0, settings=None, settings_path=None):
        new_env = RCT(rank=rank, settings_path=settings_path, settings=settings)
        new_env.rct_env.park = self.rct_env.park.clone(new_env.rct_env.settings)

        return new_env
