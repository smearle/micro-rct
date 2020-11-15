''' Render and debug. '''
import yaml
import argparse

from micro_rct.rct_env import RCTEnv



def _initialize(settings_path):
    with open(settings_path) as s_file:
        settings = yaml.load(s_file, yaml.FullLoader)
    for i in range(0, settings.get('evolution', {}).get('population_size')):

        env = RCTEnv(settings)




