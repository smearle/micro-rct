import yaml
import argparse
import multiprocessing as mp
from functools import partial
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

def get_statistics(pop):
    stats = ''
    for i, chrome in enumerate(pop):
        statline = '{} | fitness: {} | dimensions: {}'.format(i, chrome.fitness, chrome.dimensions)
        stats += statline + '\n'
    return stats

def eval_chromosome(index, pop, settings):
    chrome = pop[index]
    print('eval {}'.format(index))
    chrome.simulate(ticks=settings.get('evolution', {}).get('eval_ticks'))

def run_generation(id, pop, settings):
    print('** running generation {}'.format(id))
    # run it all. RUN IT ALLLLLLL!!!!
    eval_partial = partial(eval_chromosome, pop=pop, settings=settings)

    if settings.get('parallelism', {}).get('enabled'):
        pool = mp.Pool(settings.get('parallelism', {}).get('threads'))
        pool.map(eval_partial, [i for i in range(0, len(pop))])

        pool.close()
        pool.join()
    else:
        for i in range(0, len(pop)):
            eval_chromosome(i, pop, settings)
    # TODO map elite grid

    # TODO run mutation

    

def main(settings_path):
    pop, settings = _initialize(settings_path)
    print(len(pop))
    print('** POP BREAKDOWN **')
    print(get_statistics(pop))
    for i in range(settings.get('evolution', {}).get('gen_count')):
        run_generation(i, pop, settings)
        print(get_statistics(pop))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
