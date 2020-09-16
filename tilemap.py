
import pygame
import pygame.locals
import numpy as np
from rct_test_objects import symbol_list, symbol_dict

symbol_dict[-1] = ('Wall', '▓')

def load_tile_table(filename, width, height):
    image = pygame.image.load(filename).convert()
    image_width, image_height = image.get_size()
    tile_table = []
    for tile_x in range(0, image_width/width):
        line = []
        tile_table.append(line)
        for tile_y in range(0, image_height/height):
            rect = (tile_x*width, tile_y*height, width, height)
            line.append(image.subsurface(rect))
    return tile_table



class Map():
    # channels of map belonging to the given category
    RIDES = 0
    PATH = 1
    PEEPS = 2
    def __init__(self, park=None):
        pygame.init()
        self.screen_width = 1000
        self.screen_height = 1000
        self.map_width = park.size[0]
        self.map_height = park.size[1]
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.park = park
        self.map = park.map
        self.tile_width = self.screen_width // self.map_width
        self.tile_height = self.screen_height // self.map_height
        self.path_tile = self.load_path("tilemap/img/path_grey.png")
        self.path_tile = pygame.transform.scale(self.path_tile, (self.tile_width, self.tile_height))
        self.grass_tile = self.load_grass("tilemap/img/grass_neutral.png")
        self.grass_tile = pygame.transform.scale(self.grass_tile, (self.tile_width, self.tile_height))
        self.guest_tile = self.load_image("tilemap/img/guest.png")
        self.guest_tile = pygame.transform.scale(self.guest_tile, (self.tile_width, self.tile_height))
        self.shop_tile = self.load_shop("tilemap/img/balloon.png")
        self.shop_tile = pygame.transform.scale(self.shop_tile, (self.tile_width, self.tile_height))
        self.firstaid_tile = self.load_firstaid("tilemap/img/first aid.png")
        self.firstaid_tile = pygame.transform.scale(self.firstaid_tile, (self.tile_width, self.tile_height))
        self.drink_tile = self.load_image("tilemap/img/soda.png")
        self.drink_tile = pygame.transform.scale(self.drink_tile, (self.tile_width, self.tile_height))
        self.food_tile = self.load_image("tilemap/img/burger.png")
        self.food_tile = pygame.transform.scale(self.food_tile, (self.tile_width, self.tile_height))
        self.info_tile = self.load_info("tilemap/img/info.png")
        self.info_tile = pygame.transform.scale(self.info_tile, (self.tile_width, self.tile_height))
        self.toilet_tile = self.load_toilet("tilemap/img/toilet.png")
        self.toilet_tile = pygame.transform.scale(self.toilet_tile, (self.tile_width, self.tile_height))
        self.cin_tile = self.load_cin("tilemap/img/3D Cinema.png")
        self.cin_tile = pygame.transform.scale(self.cin_tile, (self.tile_width*2, self.tile_height*2))
        self.circus_tile = self.load_circus("tilemap/img/Circus.png")
        self.circus_tile = pygame.transform.scale(self.circus_tile, (self.tile_width*2, self.tile_height*2))
        self.crooked_tile = self.load_crooked("tilemap/img/Crooked House.png")
        self.crooked_tile = pygame.transform.scale(self.crooked_tile, (self.tile_width*2, self.tile_height*2))
        self.observation_tile = self.load_image("tilemap/img/observation_tower.png")
        self.observation_tile = pygame.transform.scale(self.observation_tile, (self.tile_width*2, self.tile_height*2))
        self.car_tile = self.load_image("tilemap/img/car_ride.png")
        self.car_tile = pygame.transform.scale(self.car_tile, (self.tile_width*10, self.tile_height*10))
        self.motion_tile = self.load_image("tilemap/img/motion_simulator.png")
        self.motion_tile = pygame.transform.scale(self.motion_tile, (self.tile_width*2, self.tile_height*2))
        self.spiral_tile = self.load_image("tilemap/img/spiral_slide.png")
        self.spiral_tile = pygame.transform.scale(self.spiral_tile, (self.tile_width*2, self.tile_height*2))
        self.magic_tile = self.load_image("tilemap/img/magic_carpet.png")
        self.magic_tile = pygame.transform.scale(self.magic_tile, (self.tile_width*2, self.tile_height*2))
        self.twist_tile = self.load_image("tilemap/img/twist.png")
        self.twist_tile = pygame.transform.scale(self.twist_tile, (self.tile_width*2, self.tile_height*2))
        self.freefall_tile = self.load_image("tilemap/img/launched_freefall.png")
        self.freefall_tile = pygame.transform.scale(self.freefall_tile, (self.tile_width*2, self.tile_height*2))
        self.ascii_tiles = {}
        

    def render_park(self, i=0, j=0):
        tile_width, tile_height = self.tile_width, self.tile_height
        self.map = self.park.map
        while i < self.map.shape[1]:
            j = 0
            while j < self.map.shape[2]:
                curr_ride_tile = self.map[0, i, j]
                if curr_ride_tile == -1:
                    curr_ride_tile = ' '
                else:
                    curr_ride_tile = symbol_list[curr_ride_tile]
                curr_path_tile = self.map[1, i, j]
                curr_peep_tile = self.map[2, i, j]
                i_pix = i*self.tile_width
                j_pix = j*self.tile_height
                self.screen.blit(self.grass_tile, (i_pix, j_pix))
                if curr_path_tile == 1:
                    self.screen.blit(self.path_tile, (i_pix, j_pix))
                if curr_ride_tile == -1:
                    pass
                elif curr_ride_tile == 's':
                    self.screen.blit(self.shop_tile, (i_pix, j_pix, i_pix+2*tile_width, j_pix+2*tile_height))
                elif curr_ride_tile == '╬':
                    self.screen.blit(self.firstaid_tile, (i_pix, j_pix))
                elif curr_ride_tile == 'º':
                    self.screen.blit(self.drink_tile, (i_pix, j_pix))
                elif curr_ride_tile == 'i':
                    self.screen.blit(self.info_tile, (i_pix, j_pix))
                elif curr_ride_tile == 'f':
                    self.screen.blit(self.food_tile, (i_pix, j_pix))
                elif curr_ride_tile == 't':
                    self.screen.blit(self.toilet_tile, (i_pix, j_pix))
                elif curr_ride_tile in '3c/~T§F¶¥':
                    pass
                else:
                    if curr_ride_tile not in self.ascii_tiles:
                        tile = pygame.font.Font(None, self.tile_height).render(curr_ride_tile, False, (255, 255, 255))
                        self.ascii_tiles[curr_ride_tile] = tile
                    else:
                        tile = self.ascii_tiles[curr_ride_tile]
                    self.screen.blit(tile, (i_pix, j_pix))

                if curr_peep_tile == 1:
                    self.screen.blit(self.guest_tile, (i_pix, j_pix))

                j += 1
            i += 1
        for ride in self.park.listOfRides:
            ride = ride[1]
            i_pos = ride.position[0] * self.tile_width
            j_pos = ride.position[1] * self.tile_height
            if ride.name == 'Cinema3D':
                self.screen.blit(self.cin_tile, (i_pos, j_pos))
            elif ride.name == 'CrookedHouse':
                self.screen.blit(self.crooked_tile, (i_pos, j_pos))
            elif ride.name == 'Circus':
                self.screen.blit(self.circus_tile, (i_pos, j_pos))
            elif ride.name == 'ObservationTower':
                self.screen.blit(self.observation_tile, (i_pos, j_pos))
            elif ride.name == 'MagicCarpet':
                self.screen.blit(self.magic_tile, (i_pos, j_pos))
            elif ride.name == 'MotionSimulator':
                self.screen.blit(self.motion_tile, (i_pos, j_pos))
            elif ride.name == 'Twist':
                self.screen.blit(self.twist_tile, (i_pos, j_pos))
            elif ride.name == 'SpiralSlide':
                self.screen.blit(self.spiral_tile, (i_pos, j_pos))
            elif ride.name == 'LaunchedFreefall':
                self.screen.blit(self.freefall_tile, (i_pos, j_pos))
            elif ride.name == 'CarRide':
                self.screen.blit(self.car_tile, (i_pos, j_pos))
        pygame.display.flip()
     #  while pygame.event.wait().type != pygame.locals.QUIT:
     #      pass



    def render_ride(self, map, i, j):
        i += 1
        j += 1
        self.render_park(i, j)

    def load_path(self, filename):
        image = pygame.image.load(filename).convert()
        rect = (0, 0, self.tile_width, self.tile_height)
        tile = image.subsurface(rect)
        return tile

    def load_grass(self, filename):
        image = pygame.image.load(filename).convert()
        rect = (0, 0, self.tile_width, self.tile_height)
        tile = image.subsurface(rect)
        return tile

    def load_shop(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        rect = (0, 0, 57, 78)
        tile = image.subsurface(rect)
        return tile
 
    def load_food(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        rect = (0, 0, 62, 54)
        tile = image.subsurface(rect)
        return tile
 
    def load_info(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        rect = (0, 0, 48, 67)
        tile = image.subsurface(rect)
        return tile

    def load_image(self, filename):
        image = pygame.image.load(filename).convert_alpha()
       #tile = image.subsurface()
        return image
 
    def load_toilet(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        rect = (0, 0, 63, 59)
        tile = image.subsurface(rect)
        return image

    def load_firstaid(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        rect = (0, 0, 65, 61)
        tile = image.subsurface(rect)
        return image

    def load_drink(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        rect = (0, 0, 65, 61)
        tile = image.subsurface(rect)
        return image

    def load_guest(self, filename):
        image = pygame.image.load(filename).convert_alpha()
        rect = (8, 5, 20, 27)
        tile = image.subsurface(rect)
        return image

    def load_crooked(self, filename, width=105, height=120):
        image = pygame.image.load(filename).convert_alpha()
        tile_y = 180
        tile_x = 5
        line = []
        rect_NE = (tile_x, tile_y, width, height)
        tile_NE = image.subsurface(rect_NE)
        tile_x += width
        rect_SE = (tile_x, tile_y, width, height)
        tile_SE = image.subsurface(rect_SE)
        tile_x += width
        rect_SW = (tile_x, tile_y, width, height)
        tile_SW = image.subsurface(rect_SW)
        tile_x += width
        rect_NW = (tile_x, tile_y, width, height)
        tile_NW = image.subsurface(rect_NW)

        return tile_NW

    def load_cin(self, filename, width=138, height=170):
        image = pygame.image.load(filename).convert_alpha()
        tile_y = 120
        tile_x = 5
        line = []
        rect_NE = (tile_x, tile_y, width, height)
        tile_NE = image.subsurface(rect_NE)
        tile_x += width
        rect_SE = (tile_x, tile_y, width, height)
        tile_SE = image.subsurface(rect_SE)
        tile_x += width
       #rect_SW = (tile_x, tile_y, width, height)
       #tile_SW = image.subsurface(rect_SW)
       #tile_x += width
        rect_NW = (tile_x, tile_y, width, height)
        tile_NW = image.subsurface(rect_NW)

        return tile_NW

    def load_circus(self, filename, width=130, height=120):
        image = pygame.image.load(filename).convert_alpha()
        tile_y = 115
        tile_x = 5
        line = []
        rect_NE = (tile_x, tile_y, width, height)
        tile_NE = image.subsurface(rect_NE)
        tile_x += width
        rect_SE = (tile_x, tile_y, width, height)
        tile_SE = image.subsurface(rect_SE)
        tile_x += width
       #rect_SW = (tile_x, tile_y, width, height)
       #tile_SW = image.subsurface(rect_SW)
       #tile_x += width
        rect_NW = (tile_x, tile_y, width, height)
        tile_NW = image.subsurface(rect_NW)

        return tile_NW


if __name__=='__main__':
    map = Map()
    map.render_park()
