''' Render and debug. '''
import yaml
import argparse

from micro_rct.rct_env import RCTEnv
from evolution.chromosome import Chromosome


def _initialize(settings_path):
    with open(settings_path) as s_file:
        settings = yaml.load(s_file, yaml.FullLoader)
    pop = []
    for i in range(0, settings.get('evolution', {}).get('population_size')):
        c = Chromosome(settings)
        pop.append(c)
    return pop, settings

def main(settings_path):
    pop, settings = _initialize(settings_path)
    print(len(pop))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
