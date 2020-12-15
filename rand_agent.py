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

    print(settings, 'thems the settings in rand_agent.py')
    env = RCT(settings=settings, rank=1)

    while True:
        env.reset()
        env.render()

        env.max_step = 1001 # so we don't hit a dedicated simulation step, and can watch builds/park sim in simultaneous action
        for j in range(500):
            env.act(env.action_space.sample())
            env.render()
        for j in range(500):
            env.step_sim()
            env.render()
        env.update_terminal_metrics()
        


if __name__ == "__main__":
    main(settings)
