import random,sys
from micro_rct.map_utility import placeRide, placePath
import random
import time
from micro_rct.park import Park
from micro_rct.path import PathFinder
from micro_rct.peeps_generator import generate
from micro_rct.rct_test_objects import object_list as ride_list
from micro_rct.rct_test_objects import symbol_list
from micro_rct.tilemap import Map
import copy

RENDER = False

def main():
   env = RCTEnv(RENDER)
   env.reset()
   env.simulate()


class RCTEnv():
    N_GUESTS = 100

    MAP_WIDTH = 30
    MAP_HEIGHT = 30
    N_ACTIONS = 30
    N_RIDES = len(ride_list)

    def __init__(self, render=True):
        self.park = Park(self.MAP_HEIGHT, self.MAP_WIDTH)
        self.RENDER = render

    def reset(self):
        placePath(self.park, margin=3)

        for _ in range(self.N_ACTIONS):
            ride_i = random.randint(0, self.N_RIDES-1)
            placeRide(self.park, ride_list[ride_i](), str(symbol_list[ride_i]))
        self.park.populate_path_net()
        path_finder = PathFinder(self.park.path_net)
        peeps = generate(self.N_GUESTS, self.park, 0.2, 0.2, path_finder)
        for p in peeps:
            self.park.updateHuman(p)

    def simulate(self, n_ticks=-1):
        frame = 0
        park_map = Map(self.park, render=self.RENDER)
        while frame < n_ticks or n_ticks == -1:
            self.park.update(frame)
            if self.RENDER:
                park_map.render_park()
            frame += 1




#def run_experiment(self, n_ticks, n_trials=20):
#    start_time = time.time()
#    for i in range(n_trials):
#        log_name = 'output_logs/guests_{}_ticks_{}_trial_{}'.format(self.N_GUESTS, n_ticks, i)
#        print(log_name)
#        orig_stdout = sys.stdout
#        f = open(log_name, 'w')
#        sys.stdout = f
#        run_trial(n_ticks)
#        sys.stdout = orig_stdout
#        f.close()
#    print('Experiment log filename: {}\n Time elapsed: {}'.format(log_name, time.time() - start_time))
#
#def run_trial(n_ticks):
#    park = Park(MAP_HEIGHT, MAP_WIDTH)
#    #place the path
#    placePath(park, margin=3)
#    park.printPark()
#    #place the ride (park, ride object, marks)
#
#    for _ in range(10):
#        ride_i = random.randint(0, N_RIDES-1)
#        placeRide(park, ride_list[ride_i], str(symbol_list[ride_i])) 
#    park.populate_path_net()
#    path_finder = PathFinder(park.path_net)
#    peeps = generate(N_GUESTS, 0.2, 0.2, path_finder)
#    park.printPark()
#    #place the guest
#
#    for p in peeps:
#        res = park.updateHuman(p)
#
#        for line in res:
#            print(line)
#    park.printPark()
#    #testing
#    frame = 0
#
#    if n_ticks == -1:
#        map = Map(park)
#        while True:
#            park.update(frame)
##           time.sleep(0.4)
#            map.render_park()
#            # NB: might overflow
#            frame += 1
#
#    map = Map(park)
#    for _ in range(n_ticks):
#        frame += 1
#        park.update(frame)
#        map.render_park()
#    del(park)
#    del(path_finder)
#    del(peeps)
#    return

if __name__ == "__main__":
    main()
