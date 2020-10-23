import argparse

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
        env.resetSim()

        # basic impassible-shop test
       #env.place_ride_tile(3, 5, -2, 0)
       #env.place_ride_tile(5, 3, -2, 0)

        for j in range(100):
            env.act(env.action_space.sample())
            env.render()
            env.delete_islands()
            env.render()
        env.resetSim()

        env.simulate(500)
        env.render()


if __name__ == "__main__":
    main(settings_path)
