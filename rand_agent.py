import argparse
import numpy as np
np.random.seed(0)

from gym_micro_rct.envs.rct_env import RCT

parser = argparse.ArgumentParser()
parser.add_argument('--settings-path',
                    '-sp',
                    default='configs/settings.yml',
                    help='path to read the settings yaml file')
args = parser.parse_args()
settings_path = args.settings_path


def main(settings):

    env = RCT(settings_path=settings, rank=1)

    env.reset()

    while True:
#       env.resetSim()
#       env.place_ride_tile(4, 1, -3, 0)
#       env.demolish_tile(3, 2)
#       env.render()

        # basic impassible-shop test
       #env.place_ride_tile(3, 5, -2, 0)
       #env.place_ride_tile(5, 3, -2, 0)

        for j in range(20):
            env.act(env.action_space.sample())
            env.render()
            env.delete_islands()
            env.render()
        env.resetSim()

        env.simulate(200)
        env.render()


if __name__ == "__main__":
    main(settings_path)
