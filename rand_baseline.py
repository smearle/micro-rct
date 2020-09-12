import random,sys
from map_utility import placeRide, placePath
import random
import time
from park import Park
from path import PathFinder
from peeps_generator import generate
from rct_test_objects import object_list as ride_list
from rct_test_objects import symbol_list


N_GUESTS = 100
RENDER = True
if RENDER:
    from tilemap import Map

MAP_WIDTH = 50
MAP_HEIGHT = 50
N_ACTIONS = 10
N_RIDES = len(ride_list)

def main():
    run_experiment(n_ticks=500)
    run_experiment(n_ticks=1000)

def run_experiment(n_ticks, n_trials=20):
    start_time = time.time()
    for i in range(n_trials):
        log_name = 'output_logs/guests_{}_ticks_{}_trial_{}'.format(N_GUESTS, n_ticks, i)
        print(log_name)
        orig_stdout = sys.stdout
        f = open(log_name, 'w')
        sys.stdout = f
        run_trial(n_ticks)
        sys.stdout = orig_stdout
        f.close()
    print('Experiment log filename: {}\n Time elapsed: {}'.format(log_name, time.time() - start_time))

def run_trial(n_ticks):
    park = Park(MAP_HEIGHT, MAP_WIDTH)
    #place the path
    placePath(park, margin=3)
    park.printPark()
    #place the ride (park, ride object, marks)

    for _ in range(10):
        ride_i = random.randint(0, N_RIDES-1)
        placeRide(park, ride_list[ride_i], str(symbol_list[ride_i])) 
    park.populate_path_net()
    path_finder = PathFinder(park.path_net)
    peeps = generate(N_GUESTS, 0.2, 0.2, path_finder)
    park.printPark()
    #place the guest

    for p in peeps:
        res = park.updateHuman(p)

        for line in res:
            print(line)
    park.printPark()
    #testing
    frame = 0

    if n_ticks == -1:
        map = Map(park)
        while True:
            park.update(frame)
#           time.sleep(0.4)
            map.render_park()
            # NB: might overflow
            frame += 1

    map = Map(park)
    for _ in range(n_ticks):
        frame += 1
        park.update(frame)
        map.render_park()
    del(park)
    del(path_finder)
    del(peeps)
    return

if __name__ == "__main__":
    main()
