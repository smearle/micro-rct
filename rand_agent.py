import argparse
import numpy as np
import yaml
np.random.seed(0)

from micro_rct.gym_envs.rct_env import RCT

parser = argparse.ArgumentParser()
parser.add_argument('--settings-path',
                    '-sp',
                    default='./configs/settings.yml',
                    help='path to read the settings yaml file')
args = parser.parse_args()
settings_path = args.settings_path
with open(settings_path) as s_file:
    settings = yaml.load(s_file, yaml.FullLoader)


def main(settings):

    env = RCT(settings=settings, rank=1)

    while True:
        env.reset()
        env.render()

        env.demolish_tile(0,1)
#       for j in range(30):
#           env.act(env.action_space.sample())
#           env.render()
        for i in range(100):
            env.step_sim()
            env.render()

        env.render()


if __name__ == "__main__":
    main(settings)
