import pygame
import math
import random

from socket import gethostbyname, gethostname # To name myself


# Classes


class cell:
    def __init__(self, world, world_dimensions, pos=(0, 0), colour=(255, 0, 0), starting_mass=50):
        self.pos = list(pos)
        self.colour = colour
        self.mass = starting_mass
        self.radius = starting_mass
        self.world_surface = world
        self.world_geometry = world_dimensions

        self.speed = 10 # for testing - will be a function later


    def __str__(self):
        '''
        Return a string from which this blob can be recreated
        '''
        out = {}

        out["pos"] = self.pos
        out["colour"] = self.colour
        out["mass"] = self.mass
        
        return str(out)


    def config(self, new_data):
        '''
        Configure a blob's attributes based on a dict provided by the above
        '''
        new_data = new_data

        self.pos = new_data["pos"]
        self.colour = new_data["colour"]
        self.mass = new_data["mass"]


    def display(self):
        pygame.draw.circle(self.world_surface, self.colour, self.pos, self.radius, self.radius)

    
    def move(self, new_pos):
        '''
        Update blob's coordinates to a new location
        Takes an array like (x,y) of coords
        '''
        self.pos = list(new_pos)


    def update_mass(self, mass):
        '''
        Update our mass and adjust speed as necessary
        '''
        self.mass = mass
        # TODO adjust speed

    

class player_cell(cell):
    def __init__(self, display_xy, *args):
        super().__init__(*args)
        self.d_x = 0
        self.d_y = 0
        self.display_geometry = display_xy

        self.move = self.key_move  # Set move function depending on mouse or keyboard
        
        # self.mouse_pos = self.pos
        self.camera_pos = [self.pos[0] + (display_xy[0] // 2), self.pos[1] + (display_xy[1] // 2)]


    def set_mouse_mode(self, activate=True):
        if activate:
            self.move = self.mouse_move
        else:
            self.move = self.key_move


    def mouse_move(self):
        '''
        Control Movement Based on Mouse
        '''

        self.mouse_pos = pygame.mouse.get_pos()

        rel_x = self.mouse_pos[0] - (self.display_geometry[0] // 2)
        rel_y = self.mouse_pos[1] - (self.display_geometry[1] // 2)

        angle = math.atan2(rel_y, rel_x)

        self.d_x = self.speed * math.cos(angle)
        self.d_y = self.speed * math.sin(angle)


        ##  For Mouse control
        self.pos = [self.pos[0] + self.d_x, self.pos[1] + self.d_y]


        # Prevent wiggling about the cursor caused by over movement
        if abs(self.pos[0] - self.mouse_pos[0]) <= abs(self.d_x):
            self.pos[0] = self.mouse_pos[0]

        if abs(self.pos[1] - self.mouse_pos[1]) <= abs(self.d_y):
            self.pos[1] = self.mouse_pos[1]

        self.camera_pos = [ - self.pos[0] + self.display_geometry[0] // 2, - self.pos[1] + self.display_geometry[1] // 2]

        self.wall_detect()


    def key_move(self):

        ##  Move with keyboard
        pressed_keys = pygame.key.get_pressed()

        if pressed_keys[pygame.K_w]:
            # self.camera_pos[1] += self.speed
            self.pos[1] -= self.speed

        if pressed_keys[pygame.K_a]:
            # self.camera_pos[0] += self.speed
            self.pos[0] -= self.speed

        if pressed_keys[pygame.K_s]:
            # self.camera_pos[1] -= self.speed
            self.pos[1] += self.speed

        if pressed_keys[pygame.K_d]:
            # self.camera_pos[0] -= self.speed
            self.pos[0] += self.speed

        self.camera_pos = [ - self.pos[0] + self.display_geometry[0] // 2, - self.pos[1] + self.display_geometry[1] // 2]

        self.wall_detect()


    def wall_detect(self):
        # Validate edge collision
        if self.pos[0] < 0: # Left
            self.pos[0] = 0
            self.camera_pos[0] = self.display_geometry[0] // 2

        if self.pos[1] < 0: # Top
            self.pos[1] = 0
            self.camera_pos[1] = self.display_geometry[1] // 2

        if self.pos[0] > self.world_geometry[0] : # Right
            self.pos[0] = self.world_geometry[0]
            self.camera_pos[0] = - self.world_geometry[0] + self.display_geometry[0] // 2

        if self.pos[1] > self.world_geometry[1] : # Bottom
            self.pos[1] = self.world_geometry[1]
            self.camera_pos[1] = - self.world_geometry[1] + self.display_geometry[1] // 2


    def translate(self, new_pos):
        '''
        simple quick translation for testing
        '''
        self.pos[0] += new_pos[0]
        self.pos[1] += new_pos[1]
        self.camera_pos[0] -= new_pos[0]
        self.camera_pos[1] -= new_pos[1]


class game:

    def __init__(self, run_flag=None):
        '''
        Create a game instance
        Allows for an optional running flag to be provided
        which should be a threading.event object
        '''
                
        # Variables

        DISPLAY_WIDTH = 1280
        DISPLAY_HEIGHT = 720
        self.DISPLAY_GEOMETRY = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.UPS = 50    # updates per second

        self.MY_ID = str(gethostbyname(gethostname()))

        

        self.parameters = {
            "world_width"   : 1000,
            "world_height"  : 1000,
            "mouse_mode"    : False,
            "player_colour" : "#4ef35a",
            "player_name"   : "Jad",
            "random_seed"   : random.randint(0, 10000),
            "rnd_count"     : 0
        }

        WORLD_WIDTH = self.parameters["world_width"]
        WORLD_HEIGHT = self.parameters["world_height"]
        self.WORLD_GEOMETRY = (WORLD_WIDTH, WORLD_HEIGHT)


        # Create world

        self.game_map = pygame.Surface(self.WORLD_GEOMETRY)

        self.blobs = {}

        print("[GAME]:Created game instance")

        if run_flag:
            self.running_flag = run_flag
            print("[GAME]:Run flag provided")

        else:
            self.running_flag = None



    def configure_game(self, config_pack):
        '''
        Configure the game's setup to match a multiplayer server / customise the game
        config_pack is blobs -> dot_list -> parameters

        blobs come in a string of a dictionary
        dots come as list
        parameters come as a dictionary
        '''
        new_blobs, dot_list, new_parameters = config_pack

        # Create new blobs:
        # new blobs is like "ip_address:{keys:info}," repeated arbitrarily

        while len(new_blobs) >= 3: # there wont be more than 3 commas or spaces at the end
            name, new_blobs = new_blobs[:new_blobs.index(":")], new_blobs[new_blobs.index(":")+1:]
            info, new_blobs = new_blobs[:new_blobs.index("}")+1], new_blobs[new_blobs.index("}")+1:]

            self.blobs[name] = cell(self.game_map, self.WORLD_GEOMETRY)
            self.blobs[name].config(eval(info)) # sometimes eval gives dodgy results but data is consistent enough here


        # Add dots
        # TODO spawn dots
        dot_list = dot_list


        # Merge sets of parameters
        self.parameters = self.parameters | eval(new_parameters)

        print("[GAME]:Game Configured")


    def create_blob(self, controller, controller_type="networked"):
        '''
        Create a blob of a given type and designate its controller
        '''
        self.blobs[controller] = cell(self.game_map, self.WORLD_GEOMETRY)
        print(f"[GAME]:Created Blob ID:{controller}")

    
    def disconnect_blob(self, controller):
        '''
        Delete a designated blob from the game
        '''
        del self.blobs[controller]


    def info_for_new(self):
        '''
        Return array of info to send to a new player
        I.E. Parameters dictionary and blobs and stuff
        blobs -> dot_list -> parameters

        blobs come in a dictionary of name: blob string
        dots come as list
        parameters come as a dictionary
        '''

        # first part is our blobs and a string to recreate them
        blobs_out = "" #"{"
        for i in self.blobs:
            blobs_out += f"{i}:{str(self.blobs[i])},"
        # blobs_out += "}"


        # now append the dot_list
        # TODO
        dots_out = "wee"


        # now add parameters
        params_out = str(self.parameters)

        out = [blobs_out, dots_out, params_out]

        print(f"[GAME]:Generated new intro packet")

        return out


    def data_to_send(self):
        '''
        Generate data to send to the server when we update something
        Data is new mass of player blob, and location
        '''
        out = f"{self.MY_ID},{self.blobs[self.MY_ID].mass},"    # our name, our mass
        out += f"{self.blobs[self.MY_ID].pos[0]},{self.blobs[self.MY_ID].pos[1]}" # our x, our y

        return out


    def process_player_move(self, data):
        '''
        Process an update for movement of a player blob
        I.E. receiving end of data sent via above method
        '''
        # Transform data
        blob, mass, pos_x, pos_y = data.split(",")
        pos = (int(pos_x), int(pos_y))
        mass = int(mass)

        # Use data to relocate blob
        self.blobs[blob].update_mass(mass)
        self.blobs[blob].move(pos)


    def is_running(self):
        '''
        Return True if the game is in its main loop
        Otherwise returns false
        '''
        return self.running_flag.isSet()


    def run(self):
        '''
        Run the game
        '''
        ##  Key Variables
        pygame.init()

        print("[GAME]:Game Run?")

        
        WORLD_WIDTH = self.parameters["world_width"]
        WORLD_HEIGHT = self.parameters["world_height"]
        self.WORLD_GEOMETRY = (WORLD_WIDTH, WORLD_HEIGHT)



        ##  configure display and pygame settings
        game_display = pygame.display.set_mode(self.DISPLAY_GEOMETRY)
        game_display.fill((250, 250, 250))

        pygame.display.set_caption("Jario")


        clock = pygame.time.Clock()


        ##  Creating things!



        # Create PLayer
        player_colour = self.parameters["player_colour"]
        player_centre = (0, 0) #(- WORLD_WIDTH // 2, - WORLD_HEIGHT // 2)


        player = player_cell(self.DISPLAY_GEOMETRY, self.game_map, self.WORLD_GEOMETRY, player_centre, player_colour)

        ##  Mouse Mode toggle will be in menu or something later
        mouse_mode = self.parameters["mouse_mode"]

        if mouse_mode:
            player.set_mouse_mode()

        # player.translate((1000, 100))

        self.blobs[self.MY_ID] = player
        print(f"[GAME]:Player {self.MY_ID} Created")
        print(f"[GAME]:BLOBS LIST:{self.blobs}")


        alive = True
        if self.running_flag != None:
            self.running_flag.set()

        while alive:
            # remove previous instances of everything
            game_display.fill((250, 250, 250))
            self.game_map.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("[GAME]:Game Quit")
                    alive = False

                    if self.running_flag != None:
                        self.running_flag.clear()


                # print(f"[GAME]:{event}")


            # Move things
            player.move()

            # display things
            for i in self.blobs:
                self.blobs[i].display()

            # Update screen
            game_display.blit(self.game_map, player.camera_pos) # transfer game view to display
            pygame.display.update()

            clock.tick(self.UPS)

        pygame.quit()

if __name__ == "__main__":

    print("[GAME]:MAIN")
    a = game()
    a.run()