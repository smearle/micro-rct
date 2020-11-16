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


class RCT(core.Env):
    class BUILDS:
        RIDE = 0,
        PATH = len(ride_list)
        DEMOLISH = PATH + 1
    RENDER_RANK = 0
    ACTION_SPACE = 1
    N_SIM_STEP = 4
    def __init__(self, **kwargs):
        self.rank = kwargs.get('rank', 0)
        settings_path = kwargs.get('settings_path', None)
        settings = kwargs.get('settings', None)
        self.render_gui = kwargs.get('render_gui', False)
        kwargs['settings'] = settings
        if not settings:
            if settings_path != None:
                with open(settings_path) as file:
                    settings = yaml.load(file, yaml.FullLoader) 
                    kwargs['settings'] = settings
            try:
                with open(settings_path) as file:
                    settings = yaml.load(file, yaml.FullLoader)
                render_gui = settings['general']['render']
            except Exception as e:
                print(e)
                settings = {
                        'general': {
                            'render': render_gui and self.rank == RCT.RENDER_RANK,
                            'verbose': False,
                            },
                        'environment': {
                            'n_guests': 10,
                            'map_width': kwargs.get('map_width', 16),
                            'map_height': kwargs.get('map_width', 16),
                            },
                        'experiments': {}
                        }

            if self.render_gui :#and self.rank == self.RENDER_RANK:
                settings['general']['render'] = True
            else:
                self.render_gui = render_gui = False
                settings['general']['render'] = False
        self.rct_env = RCTEnv(**kwargs)
        core.Env.__init__(self)
        settings = self.rct_env.settings

        self.max_step = kwargs.get('max_step', 200)
#       print('gym-micro-rct rct_env render gui?', self.render_gui)
        self.MAP_WIDTH = settings['environment']['map_width']
        self.MAP_HEIGHT = settings['environment']['map_height']

        if self.render_gui:
#           print('render rank', render_gui, rank)
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
        # if render_gui:
        #    self.park_map = self.rct_env.render_map

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
       #self.map_space = gym.spaces.Discrete(
       #    self.MAP_WIDTH * self.MAP_HEIGHT)
        self.x_space = gym.spaces.Discrete(self.MAP_WIDTH)
        self.y_space = gym.spaces.Discrete(self.MAP_HEIGHT)
       #low = np.zeros((2))
       #high = np.array([self.MAP_WIDTH - 1, self.MAP_HEIGHT - 1])
       #self.map_space = gym.spaces.Box(low, high)
       #if False:
        self.act_space = gym.spaces.Discrete(self.N_ACT_CHAN)
        self.rotation_space = gym.spaces.Discrete(4)
       #if RCT.ACTION_SPACE == 0:
       #    self.action_space = gym.spaces.Discrete((
       #        self.MAP_WIDTH * self.MAP_HEIGHT * (self.N_ACT_CHAN + 4)))
        self.action_space = gym.spaces.MultiDiscrete(
                (self.MAP_WIDTH, self.MAP_HEIGHT, self.N_ACT_CHAN, 4)
                )
#       self.action_space = gym.spaces.Dict({
#          #'map':
#          #self.map_space,
#           'x': self.x_space,
#           'y': self.y_space,
#           'act': self.act_space,
#           'rotation': self.rotation_space
#       })
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

    def rand_connect(self):
        waypoints = [ride.entrance for ride in self.rct_env.park.rides_by_pos.values()] + [Peep.ORIGIN]
        try:
            src = waypoints.pop(random.randint(0, len(waypoints)))
            trg = waypoints.pop(random.randint(0, len(waypoints)))
        except IndexError:
        #   print('not enough potential waypoints to create connecting path')
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

            for delta in [(0,1),(1,0),(-1,0),(0,-1)]:
                x, y = curr[0] + delta[0], curr[1] + delta[1]

                if (x, y) not in checking and (x, y) not in checked and \
                    0 <= x < arr.shape[1] and 0 <= y < arr.shape[2] and \
                    arr[Map.PATH, x, y] != -1:

                    checking.append((x, y))
                # if this is an entrance, the attached ride is safe from deletion
#               if curr in rides_by_pos:
#                   ride = rides_by_pos[curr]
#                   for pos in ride.locs:
#                       if pos == curr:
#                           continue
#                       print(pos)
#                       checked.append(pos)
            checked.append((curr))


        for i in range(arr.shape[1]):
            for j in range(arr.shape[2]):
                if (i, j) not in checked and (i, j) in path_net:
                    self.demolish_tile(i, j)


    def connect_with_path(self, src, trg):
        path_seq = self.rct_env.path_finder.find_map(self.rct_env.park.map, src, trg)

        return path_seq

    def place_path_tile(self, x, y, type_i=0):
        if type_i % 2 == 0:
            map_utility.place_path_tile(self.rct_env.park, x, y)

    def place_ride_tile(self, x, y, ride_i, rotation):
        #map_utility.place_ride_tile(self.rct_env.park, x, y, ride_i)
        ride = map_utility.place_ride_tile(self.rct_env.park, x, y, ride_i,
                                    rotation)
        if not ride:
            return
        path_seq = self.connect_with_path(ride.entrance, Peep.ORIGIN)

        for pos in path_seq:
            self.place_path_tile(*pos)
        self.rct_env.park.populate_path_net()

    def demolish_tile(self, x, y):
        map_utility.try_demolish_tile(self.rct_env.park, x, y)

    def update_metrics(self):
        self.metrics = {
            'happiness': self.rct_env.park.avg_peep_happiness,
        }

    def rand_act(self):
        return self.act(self.action_space.sample())

    def reset(self):
        self.rct_env.reset()
        for i in range(np.random.randint(0, self.map_width + 1)):
            self.rand_act()
       #self.rct_env.resetSim()
        self.n_step = 0
       #for i in range(random.randint(0, 10)):
       #    self.act(self.action_space.sample())
        obs = self.get_observation()

        return obs

    def get_observation(self):
        obs = np.zeros(self.observation_space.shape)
        obs[:2, :, :] = np.clip(self.rct_env.park.map[:2, :, :] + 1, 0, 1)
        ride_obs = self.rct_env.park.map[Map.RIDE] + 1
        ride_obs = ride_obs.reshape((1, *ride_obs.shape))
        ride_obs_onehot = np.zeros(
            (len(ride_list) + 1, self.MAP_WIDTH, self.MAP_HEIGHT))
        # print(ride_obs.shape)
        # print(ride_obs_onehot.shape)
       #ride_obs_onehot.scatter(0, ride_obs, 1)
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
       #x, y = action['map']
        elif RCT.ACTION_SPACE == 1:
           #x = action['x']
            x = action[0]
           #y = action['y']
            y = action[1]
           #build = action['act']
            build = action[2]
           #rotation = action['rotation']
            rotation = action[3]
            #x = int(action['position'][0])
    #       x = (self.MAP_WIDTH - 1) / 2 + (x * (self.MAP_WIDTH - 1) / 2)
    #       y = (self.MAP_HEIGHT - 1) / 2 + (y * (self.MAP_HEIGHT - 1) / 2)
    #       x = x % self.MAP_WIDTH
    #       y = y % self.MAP_HEIGHT
    #       x, y = int(x), int(y)
            #y = int(action['position'][1])
            #print('x y build', x, y, build)
            #build = action['build']
            #       print('build', x, y, build)

        if build < len(ride_list):
            self.place_ride_tile(x, y, build, rotation)
        elif build < len(ride_list) + 1:
            self.place_path_tile(x, y)
        else:
            self.demolish_tile(x, y)
       #self.delete_islands()

    def step_sim(self):
        self.rct_env.park.update(self.n_step)
        self.update_metrics()

    def step(self, action):
        self.act(action)
       #reward = 255 - self.rct_env.park.avg_peep_happiness
       #reward = len(self.rct_env.park.rides_by_pos)
        done = self.n_step >= self.max_step
        reward = 0
        if done:
            self.rct_env.park.populate_path_net()
            for _ in range(100):
           #for _ in range(RCT.N_SIM_STEP):
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


#       print('len of pathnet', len(self.rct_env.park.path_net))

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

        for x in range(self.MAP_WIDTH):
            for y in range(self.MAP_HEIGHT):
                intsToActions[i] = [x, y]
                    #self.actionsToInts[z, x, y] = i
                i += 1
#       print('len of intsToActions: {}\n num tools: {}'.format(
#           len(intsToActcopy.deepcopy(par_game)ions), self.N_ACT_CHAN))

        return intsToActions

    def resetSim(self):
        self.rct_env.resetSim()
        self.render()

    def clone(self, rank, settings_path=None, settings=None):
        if settings_path != None:
            new_env = RCT(settings_path=settings_path, rank=rank)
        elif settings != None:
            new_env = RCT(settings=settings, rank=rank)
        new_env.rct_env.park = self.rct_env.park.clone(new_env.rct_env.settings)
       #new_env.path_finder = PathFinder(new_env.park.path_net)
       #new_env.rct_env.path_finder = self.rct_env.path_finder.clone()
       #new_env.resetSim()
#       new_env.rct_env.park.populate_path_net()
        return new_env
