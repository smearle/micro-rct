import yaml
import pygame
import os
import pickle
import time
import argparse
import pandas as pd
import random
from evolution.visualization.grid_visualizer import GridVisualizer
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


class MapElitesAnalysis:
    def __init__(self, settings_path):
        with open(settings_path) as s_file:
            self.settings = yaml.load(s_file, yaml.FullLoader)

    def convert_map_to_df(self, emap):
        df = pd.DataFrame()

        df = pd.DataFrame([[value for value in cell.elite.dimensions.values()] for cell in emap.values()], columns=[
            dimen for dimen in random.choice(list(emap.values())).elite.dimensions.keys()])
        fitness_df = pd.DataFrame(
            [cell.elite.fitness for cell in emap.values()], columns=['fitness'])
        age_df = pd.DataFrame(
            [cell.elite.age for cell in emap.values()], columns=['age'])
        replace_df = pd.DataFrame(
            [cell.replace_count for cell in emap.values()], columns=['replacement'])
        challenge_df = pd.DataFrame(
            [cell.challenge_count for cell in emap.values()], columns=['challenge'])
        df = df.join(fitness_df)
        df = df.join(age_df)
        df = df.join(replace_df)
        df = df.join(challenge_df)

        return df

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

    def calc_skip(self, df, column):
        df = df.sort_values(by=column)
        diff = df.diff(axis=0, periods=1)
        diff = diff[column]
        val = diff.iloc[diff.to_numpy().nonzero()[0]].iloc[1]
        return int(val)

    def fit_swap(self, filepath, fitness):
        write_path = os.path.join(filepath, '{}_map.html'.format(fitness))
        df = self.convert_map_to_df(self.map)
        visualizer = GridVisualizer(df)
        x = df.columns[0]
        y = df.columns[1]
        x_skip = self.calc_skip(df, x)
        y_skip = self.calc_skip(df, y)
        visualizer.visualize(x=x, y=y,
            x_skip=x_skip, y_skip=y_skip, val=fitness, write_path=write_path)
        
    def auth_drive(self):
        with open("configs/drive_mapping.yml") as contents:
            self.mapping = yaml.load(contents)
        # do some authentication with google drive
        gauth = GoogleAuth(settings_file='configs/googleapi_settings.json')
        gauth.LocalWebserverAuth()

        drive = GoogleDrive(gauth)
        return drive 
        
    def agg(self, writepath):
        """Aggregates all available .p files in the results directory
        """
        drive = self.auth_drive()
        dimensions = input("Please enter a letter for a valid dimensional combination. Here are valid choices:\n\ta : happiness_vomit\n\tb : happiness_ridediversity\n\tc : excitement_intensity\n\td : excitement_nausea\n\te : all\nEnter Choice: ")
        if dimensions != "all":

            size = input("Please select an initial size choice (small or med).\nEnter choice: ")
            cost = input("Please enter cost or no_cost.\nEnter choice: ")
            self.run_agg_function(drive, writepath, dimensions, size, cost)
        else:
            print("All dimension combos selected. Running everything...")
            for dkey, dvalue in self.mapping.items():
                for skey, svalue in self.mapping.get(dkey).items():
                    for ckey, cvalue in self.mapping.get(dkey, {}).get(skey).items():
                        print('** Doing {} {} {}'.format(dkey, skey, ckey))
                        self.run_agg_function(drive, writepath, dkey, skey, ckey)

    def run_agg_function(self, drive, writepath, dimensions, size, cost):
        agg_df = pd.DataFrame()
            
        # file_list = drive.ListFile({'q': "'{}' in parents and '{}' in parents and '{}' in parents and name = '9999.p'".format(
        #     dimensions, size, cost
        # )}).GetList()
        folder_id = self.mapping.get(dimensions, {}).get(size, {}).get(cost)
        file_list = drive.ListFile({'q': "'{}' in parents".format(folder_id)}).GetList()

        for file in file_list:
            print('title: {}, id: {}'.format(file['title'], file['id']))
            exp_id = file['id']
            print('exp_id ', exp_id)
            exp_file_list = drive.ListFile({'q': "'{}' in parents".format(exp_id)}).GetList()
            for generation_file in exp_file_list:
                if generation_file['title'] == '9999.p':
                    print('9999.p found in {}'.format(file['title']))
                    filepath = "results/{}_{}_{}_{}.p".format(dimensions, size, cost, file['title'])
                    generation_file.GetContentFile(
                        filename=filepath
                    )
                    print("Loading map {}".format(filepath))
                    with open(filepath, 'rb') as f:
                            emap = pickle.load(f)
                    columns = [dimen for dimen in random.choice(list(emap.values())).elite.dimensions.keys()]
                    df = self.convert_map_to_df(emap)
                    # remove emap from memory
                    del emap
                    os.remove(filepath)
                    agg_df = pd.concat([agg_df, df]).groupby(columns, as_index=False)["fitness"].max()
        visualizer = GridVisualizer(agg_df)
        x = agg_df.columns[0]
        y = agg_df.columns[1]
        x_skip = self.calc_skip(agg_df, x)
        y_skip = self.calc_skip(agg_df, y)

        writepath = os.path.join(writepath, '{}_{}_{}.html'.format(dimensions, size, cost))
        visualizer.visualize(x=x, y=y,
            x_skip=x_skip, y_skip=y_skip, val='fitness', write_path=writepath)

    def run(self):
        # an input looper that can run many commands
        initial_action = input('Enter "aggregate" to perform an aggregation, or "analyze" to perform analysis on a single generation.\nEnter command: ')
        if initial_action == "analyze":
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
                'Please enter a command (viz-1, viz-all, fit-swap, query, help, or quit).\nEnter command: ')

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
                    elif cmd == 'fit-swap':
                        print('* Fitness-Swap visualization mode enabled...')
                        fitness = input("Please select one of the following value alternatives to visualize:\n* replacement\n* challenge\n* age\n")
                        if fitness not in ['replacement', 'challenge', 'age']:
                            print('Sorry, this is not a valid command.')
                        print("* Valid command. Generating a new elite map using {} as an alternate value...".format(fitness))
                        self.fit_swap(filepath, fitness)
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
                    'Please enter a command (viz-1, viz-all, fit-swap, query, help, or quit): ')
            print('Goodbye for now!')
        elif initial_action == "aggregate":
            filepath = self.settings.get('evolution', {}).get('save_path')
            self.agg(filepath)



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
