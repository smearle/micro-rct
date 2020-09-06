import random,sys
from map_utility import *
import random

from peeps_path_finding import *


N_GUESTS = 100

MAP_WIDTH = 50
MAP_HEIGHT = 50
N_ACTIONS = 10
N_RIDES = len(ride)

def main():
    run_experiment(n_ticks=500)
    run_experiment(n_ticks=1000)

def run_experiment(n_ticks, n_trials=20):
    for i in range(n_trials):
        log_name = 'output_logs/guests_{}_ticks_{}_trial_{}'.format(N_GUESTS, n_ticks, i)
        orig_stdout = sys.stdout
        f = open(log_name, 'w')
        sys.stdout = f
        run_trial(n_ticks)
        sys.stdout = orig_stdout
        f.close()

def run_trial(n_ticks):
    park = initPark(MAP_HEIGHT, MAP_WIDTH)
    peeps = generate(N_GUESTS, 0.2, 0.2)
    #place the path
    placePath(park, margin=3)
    park.printPark()
    #place the ride (park, ride object, marks)

    for _ in range(10):
        ride_i = random.randint(0, N_RIDES-1)
        placeRide(park, ride[ride_i], str(symbol_list[ride_i])) 
    park.printPark()
    #place the guest

    for p in peeps:
        res = park.updateHuman(p)

        for line in res:
            print(line)
    park.printPark()
    #testing
    frame = 0

    for _ in range(n_ticks):
        frame +=1
        park.update(frame)

    return

if __name__ == "__main__":
    main()
