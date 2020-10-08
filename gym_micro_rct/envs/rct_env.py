import copy
import os
import random
import sys
import time

import gym
import numpy as np
import torch
import yaml
from gym import core
from micro_rct import map_utility
from micro_rct.map_utility import placePath, placeRide
from micro_rct.park import Park
from micro_rct.path import PathFinder
from micro_rct.peeps_generator import generate
from micro_rct.rct_env import RCTEnv
from micro_rct.rct_test_objects import object_list as ride_list
from micro_rct.rct_test_objects import symbol_list
from micro_rct.tilemap import Map


def main(settings):

    env = RCT(settings)

    while True:
        env.reset()

        for i in range(10000):
            env.step(env.action_space.sample())

            if env.render_gui:
                env.render()


class RCT(core.Env):
    def __init__(self, settings_path=None, **kwargs):
        if settings_path is not None:
            with open(settings_path) as file:
                settings = yaml.load(file, yaml.FullLoader)
        else:
            settings = None
        self.rct_env = RCTEnv(settings, **kwargs)
        core.Env.__init__(self)
        settings = self.rct_env.settings
        render_gui = settings['general']['render']
        rank = kwargs.get('rank', 0)
        self.max_step = kwargs.get('max_step', 200)
        self.render_gui = render_gui
#       print('gym-micro-rct rct_env render gui?', self.render_gui)
        self.MAP_WIDTH = settings['environment']['map_width']
        self.MAP_HEIGHT = settings['environment']['map_height']

        if render_gui:
#           print('render rank', render_gui, rank)
            pass

        self.width = self.map_width = self.MAP_WIDTH

        if render_gui:
            import pygame
            pygame.init()
            screen_width = 1000
            screen_height = 1000
            self.screen = pygame.display.set_mode(
                (screen_width, screen_height))
        else:
            self.screen = None
        self.render_map = None
        self.n_step = 0
        self.metric_trgs = {
            'happiness': 255,
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
        # if render_gui:
        #    self.park_map = self.rct_env.render_map

        self.park = self.rct_env.park
        N_CHAN = len(ride_list) + 3  # path and peeps, lack of ride
        obs_shape = (N_CHAN, self.MAP_WIDTH, self.MAP_HEIGHT)
        low = np.zeros(obs_shape)
        high = np.ones(obs_shape)
        self.observation_space = gym.spaces.Box(low, high)
        act_shape = (2)
        low = np.zeros(act_shape)
        high = np.zeros(act_shape)
        high[0] = self.MAP_WIDTH
        high[1] = self.MAP_HEIGHT
        self.N_ACT_CHAN = len(ride_list) + 2
        self.action_space = gym.spaces.Discrete(
            self.MAP_WIDTH * self.MAP_HEIGHT * self.N_ACT_CHAN)
        self.entrance_pos_space = gym.spaces.Discrete(4)
        self.action_space = gym.spaces.Dict({
            'map':
            self.action_space,
            'entrance_pos':
            self.entrance_pos_space
        })
        # self.action_space = gym.spaces.Dict({
        #    'position': gym.spaces.Box(low, high),
        #    # path
        #    'build': gym.spaces.Discrete(len(ride_list) * 3),
        #    })
        self.place_rand_path_net()
        self.ints_to_actions = self.mapIntsToActions()

    def configure(self):
        pass

    def place_rand_path_net(self):
        pass

    def place_path_tile(self, x, y, type_i=0):
        if type_i % 2 == 0:
            map_utility.place_path_tile(self.rct_env.park, x, y)

    def place_ride_tile(self, x, y, ride_i, entrance_pos):
        #map_utility.place_ride_tile(self.rct_env.park, x, y, ride_i)
        map_utility.place_ride_tile(self.rct_env.park, x, y, ride_i,
                                    entrance_pos)

    def demolish_tile(self, x, y):
        map_utility.demolish_tile(self.rct_env.park, x, y)

    def update_metrics(self):
        self.metrics = {
            'happiness': self.rct_env.park.score,
        }

    def reset(self):
        self.rct_env.reset()
        self.n_step = 0
        obs = self.get_observation()

        return obs

    def get_observation(self):
        obs = np.zeros(self.observation_space.shape)
        obs[:2, :, :] = torch.Tensor(self.rct_env.park.map[:2, :, :])
        ride_obs = torch.LongTensor(self.rct_env.park.map[Map.RIDE] + 1)
        ride_obs = ride_obs.reshape((1, *ride_obs.shape))
        ride_obs_onehot = torch.zeros(
            len(ride_list) + 1, self.MAP_WIDTH, self.MAP_HEIGHT)
        # print(ride_obs.shape)
        # print(ride_obs)
        # print(ride_obs_onehot.shape)
        ride_obs_onehot.scatter(0, ride_obs, 1)
        obs[2:, :, :] = ride_obs_onehot

        return obs

    def act(self, action):
        build, x, y = self.ints_to_actions[action['map']]
        entrance_pos = action['entrance_pos']
        #print('action', action)
        #x = int(action['position'][0])
        #y = int(action['position'][1])
        #print('x y build', x, y, build)
        #build = action['build']
        #       print('build', x, y, build)

        if build < len(ride_list):
            self.place_ride_tile(x, y, build, entrance_pos)
        elif build < len(ride_list) + 1:
            self.place_path_tile(x, y)
        else:
            self.demolish_tile(x, y)

    def step_sim(self):
        self.rct_env.park.update(self.n_step)
        self.update_metrics()

    def step(self, action):
        self.act(action)
        self.step_sim()
        self.n_step += 1
        obs = self.get_observation()
        reward = self.rct_env.park.score / self.max_step
        done = self.n_step >= self.max_step
        info = {}

        if self.render_gui:
            self.render()

        return obs, reward, done, info


#       print('len of pathnet', len(self.rct_env.park.path_net))

    def render(self, mode='human', close=False):
        self.rct_env.render_map.render_park()
        self.rct_env.park.printPark()

    def simulate(self, n_ticks=-1):
        return self.rct_env.simulate(n_ticks)
#       frame = 0
#       park_map = Map(self.rct_env.park, render=self.render_gui)

#       while frame < n_ticks or n_ticks == -1:
#           self.rct_env.park.update(frame)
#           park_map.render_park()
#           frame += 1

    def mapIntsToActions(self):
        ''' Unrolls the action vector in the same order as the pytorch model
        on its forward pass.'''
        intsToActions = {}
       #chunk_width = 1
        i = 0

        for z in range(self.N_ACT_CHAN):
            for x in range(self.MAP_WIDTH):
                for y in range(self.MAP_HEIGHT):
                    intsToActions[i] = [z, x, y]
                    #self.actionsToInts[z, x, y] = i
                    i += 1
#       print('len of intsToActions: {}\n num tools: {}'.format(
#           len(intsToActcopy.deepcopy(par_game)ions), self.N_ACT_CHAN))

        return intsToActions

    def resetSim(self):
        self.rct_env.resetSim()

    def clone(self, settings_path):
        new_env = RCT(settings_path=settings_path)
        new_env.rct_env.park = copy.deepcopy(self.rct_env.park)
        new_env.rct_env.path_finder = copy.deepcopy(self.rct_env.path_finder)
        return new_env
