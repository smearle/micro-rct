import yaml
import pygame
import os
import pickle
import time
import argparse


class MapElitesAnalysis:
    def __init__(self, settings_path):
        with open(settings_path) as s_file:
            self.settings = yaml.load(s_file, yaml.FullLoader)

    def render_elites(self, filepath):
        for dim, cell in self.map.items():
            elite = cell.elite.clone()
            elite.settings['general']['render'] = True
            elite.rct.render_gui = True
            elite.rct.rct_env.set_rendering(True)
            elite.rct.rct_env.resetSim()
            elite.rct.rct_env.render_map.render_park()
            img = elite.rct.rct_env.screen
            img_name = '{}.png'.format(dim)
            # with open(os.path.join(filepath, img_name), 'w+') as save_file:
            pygame.image.save(img, os.path.join(
                filepath.split('.')[0], img_name))

    def get_map_dimensions(self):
        key = self.map.values()[0]

    def find_cell(self, x, y):
        zero_key = list(self.map.keys())[0]
        zero_key = zero_key.split(', ')
        x_title = self.clean_dimen(zero_key[0].split(': ')[0])
        y_title = self.clean_dimen(zero_key[1].split(': ')[0])

        try:
            cell = self.map['{{\"{}\": {}, \"{}\": {}}}'.format(
                x_title, x, y_title, y)]
            return cell
        except Exception as e:
            print(e)
            print('Invalid cell!')
            print('Available cells:\n{}'.format(self.map.keys()))
            return None

    def clean_dimen(self, dimen):
        dimen = dimen.replace('{', '')
        dimen = dimen.replace('}', '')
        dimen = dimen.replace('\"', '')
        return dimen

    def render_elite(self, filepath, x_dimen, y_dimen):
        elite = self.find_cell(x_dimen, y_dimen).elite.clone()
        if elite is None:
            return
        elite.settings['general']['render'] = True
        elite.rct.render_gui = True
        elite.rct.rct_env.set_rendering(True)
        elite.rct.rct_env.resetSim()
        elite.rct.rct_env.render_map.render_park()
        img = elite.rct.rct_env.screen
        img_name = '{}_{}.png'.format(x_dimen, y_dimen)
        # with open(os.path.join(filepath, img_name), 'w+') as save_file:
        pygame.image.save(img, os.path.join(
            filepath.split('.')[0], img_name))

    def query_elite(self, x_dimen, y_dimen):
        cell = self.find_cell(x_dimen, y_dimen)
        elite = cell.elite
        if elite is None:
            print('elite is none')
            return
        stats = elite.get_stats()
        stats["challenge count"] = cell.challenge_count
        stats["generation filled"] = cell.gen
        stats["replace count"] = cell.replace_count
        stats["dimensions"] = cell.dimensions
        for key, value in stats.items():
            print('{}: {}'.format(key, value))

    def run(self):
        # an input looper that can run many commands
        gen_id = input(
            'Please enter the generation number you wish to analyze: ')
        print('Loading generation. Please wait...')

        filepath = self.settings.get('evolution', {}).get('save_path')
        filepath = os.path.join(filepath, '{}'.format(gen_id))
        readpath = '{}.p'.format(filepath)
        os.makedirs(filepath.split('.')[0], exist_ok=True)
        with open(readpath, 'rb') as f:
            self.map = pickle.load(f)
        print('Generation loaded')

        cmd = input(
            'Please enter a command (viz-1, viz-all, query, help, or quit): ')

        while cmd != 'quit':
            try:
                if cmd == 'viz-1':
                    print('* Single-chromosomal visualization mode enabled...')

                    x = input(
                        'Please enter the x-dimension value of the chromosome: ')
                    y = input(
                        'Please enter the y-dimension value of the chromosome: ')

                    print('** Rendering...')
                    self.render_elite(filepath, x, y)
                elif cmd == 'viz-all':
                    print('* Multi-chromosomal visualization mode enabled...')
                    print(
                        '* Multi-chromosomal visualization rendering process initiated...')
                    t = time.time()
                    self.render_elites(filepath)
                    e = time.time()
                    print(
                        '* Multi-chromosomal visualization completed in {} minutes...'.format((e-t)/60))
                elif cmd == 'query':
                    print('* Query mode enabled...')

                    x = input(
                        'Please enter the x-dimension value of the chromosome: ')
                    y = input(
                        'Please enter the y-dimension value of the chromosome: ')

                    print('** Query information below...')
                    self.query_elite(x, y)
                elif cmd == 'help':
                    print('To use this tool, enter one of the following commands:')
                    print('* \"viz-1\": vizualizes a specified cell\'s elite')
                    print(
                        '* \"viz-all\": vizualizes all of the elites in the map (caution! this may take a while!)')
                    print(
                        '* \"query\": displays metric information about a specified cell\'s elite')
                    print('* \"help\": displays this help text about all the commands')
                    print('* \"quit\": quits the program immediately')
            except Exception as e:
                print(e)
            cmd = input(
                'Please enter a command (viz-1, viz-all, query, help, or quit): ')
        print('Goodbye for now!')


def main(settings_path):
    with open(settings_path) as s_file:
        settings = yaml.load(s_file, yaml.FullLoader)
    analyzer = MapElitesAnalysis(settings_path)
    analyzer.run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings-path', '-sp', default='configs/settings.yml',
                        help='path to read the settings yaml file')
    args = parser.parse_args()
    settings_path = args.settings_path

    main(settings_path)
