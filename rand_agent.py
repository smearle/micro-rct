from gym_micro_rct.envs.rct_env import main
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--settings-path', '-sp', default='configs/settings.yml', help='path to read the settings yaml file')
args = parser.parse_args()
settings_path = args.settings_path

main(settings_path)

