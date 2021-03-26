import pygame
import pygame_gui
import pygame.font
import math
import random
import threading


from socket import gethostbyname, gethostname # To name myself
from time import sleep


# Classes


class cell:
    def __init__(self, game, pos=(0, 0), colour=None, starting_mass=500):

        self.pos    = list(pos)

        if colour == None:
            self.colour = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            self.colour = colour

        self.mass   = starting_mass
        self.score  = starting_mass
        self.name   = "Unnamed"
        self.id     = self.name

        self.is_bloblet = False
        self.is_dead    = False

        self.radius = 10
        self.update_rad()

        self.game = game
        self.sub_blobs = set()

        self.speed = 10 
        self.update_speed()

        self.title_surface = self.game.font.render(self.name, True, self.game.parameters["font_colour"])


    def __str__(self):
        '''
        Return a string from which this blob can be recreated
        '''
        out = {}

        out["pos"] = self.pos
        out["colour"] = self.colour
        out["mass"] = self.mass
        out["score"] = self.score
        out["name"] = self.name
        
        return str(out)


    def config(self, new_data):
        '''
        Configure a blob's attributes based on a dict provided
        '''

        self.pos = new_data["pos"]
        self.colour = new_data["colour"]
        self.set_mass(new_data["mass"])
        self.score = new_data["score"]
        self.set_name(new_data["name"])


    def set_name(self, name):
        '''
        Set ourselves a name
        '''
        self.name = name
        self.title_surface = self.game.font.render(self.name, False, self.game.parameters["font_colour"])


    def display(self):
        pygame.draw.circle(self.game.game_map, self.colour, self.pos, self.radius, self.radius)
        title_pos = (self.pos[0] - self.title_surface.get_rect().center[0], self.pos[1] - self.title_surface.get_rect().center[1])
        self.game.game_map.blit(self.title_surface, title_pos)

    
    def place(self, new_pos):
        '''
        Update blob's coordinates to a new location
        Takes an array like (x,y) of coords
        '''
        self.pos = list(new_pos)


    def wall_detect(self):
        # Validate edge collision
        if self.pos[0] < 0: # Left
            self.pos[0] = 0

        if self.pos[1] < 0: # Top
            self.pos[1] = 0

        if self.pos[0] > self.game.WORLD_GEOMETRY[0] : # Right
            self.pos[0] = self.game.WORLD_GEOMETRY[0]

        if self.pos[1] > self.game.WORLD_GEOMETRY[1] : # Bottom
            self.pos[1] = self.game.WORLD_GEOMETRY[1]


    def update_rad(self):
        '''
        Update our radius to what it should be based on our mass
        '''
        self.radius = 2 * int(math.sqrt(self.mass / math.pi))


    def update_speed(self):
        '''
        Update our speed based on our mass
        '''
        self.speed = -0.5 * math.log(self.mass) + 10  # * <--- I like this one


    def set_mass(self, mass):
        '''
        Set our mass to a given value and adjust speed as necessary
        '''
        self.mass = mass
        self.update_rad()

        self.update_speed()


    def set_score(self, score):
        '''
        Set our score to a given score
        '''
        self.score = score

    
    def add_mass(self, mass):
        '''
        Add to our mass a given value and adjust speed as necessary
        '''
        if self.mass + mass <= 0:
            return

        self.mass += mass
        self.update_rad()
        self.update_speed()


    def add_score(self, score):
        '''
        Add a given amount to our score
        '''
        self.score += score


    def eat(self, mass):
        '''
        We have eaten something of this mass
        '''
        self.add_mass(mass)
        self.add_score(mass)


    def was_absorbed(self, blob):
        '''
        We have died,
        Add mass to blob which ate us
        '''
        self.is_dead = True
        self.set_score(0)
        del self.game.blobs[self.id]

        blob.eat(self.mass)

        self.mass = 0


class player_cell(cell):
    def __init__(self, game, *args):
        super().__init__(game, *args)

        self.id = self.game.MY_ID

        # Count number of sub_blobs made to prevent duplicate naming
        self.sub_blobs_made = 0

        # Peak score tracked for leaderboard
        self.peak_score = self.score

        # Here to prevent crash on game start when we try to mouse move and these don't exist
        self.d_x = 0
        self.d_y = 0

        self.move = self.key_move  # Set move function depending on mouse or keyboard
        
        # self.mouse_pos = self.pos
        self.camera_pos = [self.pos[0] + (self.game.DISPLAY_GEOMETRY[0] // 2), self.pos[1] + (self.game.DISPLAY_GEOMETRY[1] // 2)]


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

        rel_x = self.mouse_pos[0] - (self.game.DISPLAY_GEOMETRY[0] // 2)
        rel_y = self.mouse_pos[1] - (self.game.DISPLAY_GEOMETRY[1] // 2)

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

        self.camera_pos = [ - self.pos[0] + self.game.DISPLAY_GEOMETRY[0] // 2, - self.pos[1] + self.game.DISPLAY_GEOMETRY[1] // 2]

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

        self.camera_pos = [ - self.pos[0] + self.game.DISPLAY_GEOMETRY[0] // 2, - self.pos[1] + self.game.DISPLAY_GEOMETRY[1] // 2]

        self.wall_detect()


    def wall_detect(self):
        # Validate edge collision
        if self.pos[0] < 0: # Left
            self.pos[0] = 0
            self.camera_pos[0] = self.game.DISPLAY_GEOMETRY[0] // 2

        if self.pos[1] < 0: # Top
            self.pos[1] = 0
            self.camera_pos[1] = self.game.DISPLAY_GEOMETRY[1] // 2

        if self.pos[0] > self.game.WORLD_GEOMETRY[0] : # Right
            self.pos[0] = self.game.WORLD_GEOMETRY[0]
            self.camera_pos[0] = - self.game.WORLD_GEOMETRY[0] + self.game.DISPLAY_GEOMETRY[0] // 2

        if self.pos[1] > self.game.WORLD_GEOMETRY[1] : # Bottom
            self.pos[1] = self.game.WORLD_GEOMETRY[1]
            self.camera_pos[1] = - self.game.WORLD_GEOMETRY[1] + self.game.DISPLAY_GEOMETRY[1] // 2


    def translate(self, new_pos):
        '''
        simple quick translation for testing
        '''
        self.pos[0] += new_pos[0]
        self.pos[1] += new_pos[1]
        self.camera_pos[0] -= new_pos[0]
        self.camera_pos[1] -= new_pos[1]


    def eat(self, mass):
        '''
        Add to our mass a given value and adjust speed as necessary
        Polymorphed here to allow tracking of peak score
        '''
        if self.mass + mass <= 0:
            return

        super().eat(mass)

        if self.score > self.peak_score:
            self.peak_score = self.score


    def split(self):
        '''
        Split our mass in half and make a new blob with it
        '''
        # Do we have enough mass?
        if self.mass > self.game.parameters["min_split_mass"]:
            new_child = sub_cell(self, self.mass // 2)
            self.mass = self.mass // 2

            child_name = f"{self.id}_{self.sub_blobs_made}"
            new_child.id = child_name

            # Record new sub_blob in blob list
            self.game.blobs[child_name] = new_child
            new_child.set_name(self.name)
            self.sub_blobs.add(new_child)
            self.sub_blobs_made += 1

            # Update stuff for new mass
            self.update_rad()
            self.update_speed()

            print("[GAME]:Sub Blob created")


    def was_absorbed(self, blob):
        '''
        If player is absorbed it's game over
        Do not allow sub_blobs to absorb their parent
        '''
        if blob in self.sub_blobs:
            # Our child has attempted to eat us!
            return

        self.is_dead = True
        self.score = 0

        # If we are absorbed, Why bother increasing mass of other blob?
        # Other blob will do that and send out their new mass

        self.mass = 0
        self.game.game_over()


class sub_cell(cell):
    '''
    Bloblet which the player can create.
    Follows player
    '''
    def __init__(self, parent, mass):

        self.parent = parent

        super().__init__(parent.game, pos=parent.pos, colour=parent.colour, starting_mass=mass)

        self.is_bloblet = True

        # Track ticks we have lived for so we can start following parent
        self.count = 0

        self.move = self.make_move_func


    def eat(self, mass):
        '''
        Eat the gieven amount of mass
        Polymorphed because we add to our own mass, but our parent's score
        '''
        self.add_mass(mass)
        self.parent.add_score(mass)

    
    def update_speed(self):
        '''
        Update our speed based on our mass.
        Polymorphed to make sub blobs faster than they should be to keep up with parents
        '''
        super().update_speed()
        self.speed *= self.parent.game.parameters["sub_blob_speed_ratio"]
        

    def move(self):
        print("[ALERT-GAME]:Sub-Blobs movement improperly assigned")


    # Move 1
    def make_move_func(self):
        '''
        Create and assign to our move method a function to propel us away from our parent in the direction they were going.
        They should have moved away, so point towards them and go
        '''
        if self.count < self.parent.game.parameters["sub_blob_wait"]:
            # Parent hasn't had time to move away
            pass


        else:
            # What direction are we going?
            target = self.parent.pos

            rel_x = target[0] - (self.pos[0] // 2)
            rel_y = target[1] - (self.pos[1] // 2)

            # Find speed in x and y
            angle = math.atan2(rel_y, rel_x)

            d_x = self.speed * math.cos(angle)
            d_y = self.speed * math.sin(angle)

            # Move func 2
            def go_target():

                self.pos[0] += d_x
                self.pos[1] += d_y
                self.wall_detect()

                if self.count < self.parent.game.parameters["sub_blob_ttl"]:
                    # Not time to follow yet
                    pass

                else:
                    self.move = self.follow_parent
                    print("[GAME]:Sub blob now following parent")

                self.count += 1

            self.move = go_target

        self.count += 1


    # Move 3
    def follow_parent(self):
        '''
        Follow our parent
        '''
        # Find this now and save locally to save repeated lookups
        parent_pos = self.parent.pos

        # Find relative displacement
        rel_x = parent_pos[0] - self.pos[0]
        rel_y = parent_pos[1] - self.pos[1]

        angle = math.atan2(rel_y, rel_x)

        # Find ratio of x to y movement that we need
        d_x = self.speed * math.cos(angle)
        d_y = self.speed * math.sin(angle)


        if int(math.dist(self.pos, parent_pos)) > self.radius + self.parent.radius:
            # We are too far, move closer
            self.pos = [self.pos[0] + d_x, self.pos[1] + d_y]


        elif (self.count < self.parent.game.parameters["sub_blob_min_life"] and
        int(math.dist(self.pos, parent_pos)) < self.radius + self.parent.radius - self.parent.game.parameters["sub_blob_overlap"]):
            # We are too young to be reabsorbed, move away
            self.pos = [self.pos[0] - d_x, self.pos[1] - d_y]


        # Check our siblings for distance / reabsorbtion 
        for sibling in self.parent.sub_blobs:
            if not sibling is self:
                self.prevent_overlap(sibling)

        self.wall_detect()
        self.count += 1


    def prevent_overlap(self, blob):
        '''
        Check distance between us and this other blob, if too close then move away.
        For use with siblings
        '''
        if int(math.dist(self.pos, blob.pos)) < self.radius + blob.radius - self.parent.game.parameters["sub_blob_overlap"]:
            # We are too close to a sibling

            # Find relative displacement
            rel_x = blob.pos[0] - self.pos[0]
            rel_y = blob.pos[1] - self.pos[1]

            angle = math.atan2(rel_y, rel_x)

            # Find ratio of x to y movement that we need
            d_x = self.speed * math.cos(angle)
            d_y = self.speed * math.sin(angle)

            self.pos = [self.pos[0] - d_x, self.pos[1] - d_y]


    def was_absorbed(self, blob):
        '''
        We were eaten
        Polymorphed here to remove ourselves from parent's sub_blobs,
        and check if blob who ate us is a sibling or our parent
        '''
        if (blob is self.parent or blob in self.parent.sub_blobs) and self.count < self.parent.game.parameters["sub_blob_min_life"]:
            # Not time to be eaten yet - we spawn inside parent
            # And it wasn't some other person who ate us
            pass

        elif blob is self.parent or blob in self.parent.sub_blobs:
            # Lower parents score before it is increased when they eat us
            self.parent.set_score(self.parent.score - self.mass)

            super().was_absorbed(blob)


        else:
            # We can increase their score
            super().was_absorbed(blob)


class game:

    def __init__(self, params={}):
        '''
        Create a game instance
        '''

        # Variables

        DISPLAY_WIDTH = 1280
        DISPLAY_HEIGHT = 720
        self.DISPLAY_GEOMETRY = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
        self.UPS = 50    # updates per second

        self.sectors_configured = False
        self.is_multiplayer = False
        self.separator = "<GAME_SEP>"
        self.null_mass = -1
        self.port = "You shouldn't see this"        # Set port for multiplayer info display

        self.MY_ID = str(gethostbyname(gethostname()))

        
        self.parameters = {
            "world_width"   : 1000,
            "world_height"  : 1000,
            "mouse_mode"    : False,
            "player_colour" : "#4ef35a",
            "player_name"   : "Jad",
            "font_size"     : 25,
            "font"          : "Small Fonts",
            "font_colour"   : (0, 0, 0),

            "random_seed"   : random.randint(0, 10000),
            "random_count"  : 0,
            "ai_limit"      : 5,
            "ai_difficulty" : 1,

            "sector_size"   : 200,
            "dot_mass"      : 10,
            "dot_radius"    : 10,
            "dot_spawn_rate": 3,
            "blob_eat_ratio": 1.3,

            "min_split_mass": 1000,
            "sub_blob_wait" : 3,
            "sub_blob_ttl"  : 20,        # Ticks until bloblets follow their parent
            "sub_blob_min_life": 300,        # Ticks until bloblets can be reabsorbed
            "sub_blob_overlap": 10,          # Overlap leeway between blobs and their children
            "sub_blob_speed_ratio": 1.2       # Coefficient of speed in sub blobs to make them faster
        }

        self.parameters = self.parameters | params

        WORLD_WIDTH = self.parameters["world_width"]
        WORLD_HEIGHT = self.parameters["world_height"]
        self.WORLD_GEOMETRY = (WORLD_WIDTH, WORLD_HEIGHT)


        # Create world

        self.game_map = pygame.Surface(self.WORLD_GEOMETRY)

        self.ai_blob_ids = set()
        self.blobs = {}

        pygame.font.init()
        self.font = pygame.font.SysFont(self.parameters["font"], self.parameters["font_size"])

        print("[GAME]:Created game instance")

        self.running_flag = threading.Event()
        self.running_flag.clear()


    def game_over(self):
        '''
        Game is over :(
        Stop the main loop
        '''
        # Stop main loop
        game_over_image = pygame.image.load("resources/images/game_over.png") # size is (597, 84)
        self.running_flag.clear()

        # Find coords to center the game over image
        coords = ((self.DISPLAY_GEOMETRY[0] - game_over_image.get_rect().size[0]) // 2, (self.DISPLAY_GEOMETRY[1] - game_over_image.get_rect().size[1]) // 2)

        self.game_display.blit(game_over_image, coords)
        pygame.display.update()

        print("[GAME]:Game over triggered")

        sleep(1.5)


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
            name, new_blobs = new_blobs[:new_blobs.index(":")].removeprefix(","), new_blobs[new_blobs.index(":")+1:]
            info, new_blobs = new_blobs[:new_blobs.index("}")+1], new_blobs[new_blobs.index("}")+1:] # These come in the blob description

            self.create_blob(name)
            self.blobs[name].config(eval(info)) # sometimes eval gives dodgy results but data is consistent enough here


        # Add dots

        self.configure_sectors()

        # Place each dot in appropriate sector
        for dot in eval(dot_list):
            self.place_dot(dot)


        # Merge sets of parameters
        self.parameters = self.parameters | eval(new_parameters)

        print("[GAME]:Game Configured")


    def set_multiplayer(self, host=None):
        '''
        It is useful knowing whether we are a multiplayer game
        '''
        self.is_multiplayer = True

        # Assume we are the host until told otherwise
        self.host_name = self.MY_ID
        if host:
            self.host_name = host

        print("[GAME]:We are playing multiplayer")


    def configure_sectors(self):
        '''
        Establish the sector dictionary for the map.
        '''
        # Determine width and height in terms of sectors
        self.sectors_wide = self.parameters["world_width"] // self.parameters["sector_size"]
        self.sectors_high = self.parameters["world_height"] // self.parameters["sector_size"]

        # Create sector dictionary
        self.sectors = {}
        
        for x in range(self.sectors_wide + 1):
            for y in range(self.sectors_high + 1):
                self.sectors[(x, y)] = []

        self.sectors_configured = True
        print(f"[GAME]:Configured {self.sectors_wide * self.sectors_high} sectors")


    def spawn_dots(self, count=1):
        '''
        Randomly spawn a given number of dots, incrementing random count accordingly
        '''
        for _ in range(count):
            # Seed the randomness module
            seed = self.parameters["random_seed"] + self.parameters["random_count"]
            self.parameters["random_count"] += 1
            random.seed(seed)

            # Generate coordinates
            x = random.randint(0, self.parameters["world_width"])
            y = random.randint(0, self.parameters["world_height"])

            # Generate a colour for this dot
            colour = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

            self.place_dot((x, y, colour))

        if count > 1:
            print(f"[GAME]:Spawned {count} dots")


    def continuous_dot_spawn(self):
        '''
        Spawn dots every second depending on configured dot spawn rate.
        '''
        self.running_flag.wait()
        print(f"[GAME]:Continuous dot spawn enabled rate:{self.parameters['dot_spawn_rate']}")

        while self.running_flag.isSet():
            sleep(1/self.parameters["dot_spawn_rate"])
            self.spawn_dots(1)


    def place_dot(self, dot):
        '''
        Place a dot in its appropriate sector
        '''
        # Find relevant sector
        sector_x = dot[0] // self.parameters["sector_size"]
        sector_y = dot[1] // self.parameters["sector_size"]

        # Put dot in sector
        self.sectors[(sector_x, sector_y)].append(dot)


    def create_blob(self, controller):
        '''
        Create a blob of a given type and designate its controller
        '''
        self.blobs[controller] = cell(self)
        self.blobs[controller].id = controller
        print(f"[GAME]:Created Blob ID:{controller}")

    
    def disconnect_blob(self, controller):
        '''
        Delete a designated blob from the game
        '''
        for bloblet in self.blobs[controller].sub_blobs:
            del self.blobs[bloblet.id]

        del self.blobs[controller]


    def check_eat_food(self, blob):
        '''
        Look around a blob and see if it has eaten any nearby dots.
        If so, delete the dot and tell the blob that it has eaten something
        '''
        # Find blob sector coords
        blob_x, blob_y = blob.pos
        sector_x, sector_y = int(blob_x // self.parameters["sector_size"]), int(blob_y // self.parameters["sector_size"])

        # Calculate blob size in terms of sectors, add one to allow blob overlapping sector boundaries
        radius_in_sectors = blob.radius // self.parameters["sector_size"] + 1


        # Determine max and min sector coords to check
        # Make sure we don't exceed or undercut sector coords, i.e. reference negative coords
        if (min_x := sector_x - radius_in_sectors) < 0:
            min_x = 0
        if (max_x := sector_x + radius_in_sectors) > self.sectors_wide:
            max_x = self.sectors_wide

        if (min_y := sector_y - radius_in_sectors) < 0:
            min_y = 0
        if (max_y := sector_y + radius_in_sectors) > self.sectors_high:
            max_y = self.sectors_high

        # Start looking
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):

                # Check every dot in each sector
                for index, dot in enumerate(self.sectors[(x,y)]):


                    # Eat the dot or display the dot?
                    if math.dist((blob_x, blob_y), (dot[0], dot[1])) < blob.radius:
                        # We are close enough to eat the dot
                        blob.eat(self.parameters["dot_mass"])
                        del self.sectors[(x,y)][index]


    def check_eat_blob(self, blob):
        '''
        Check if a specific blob is able to eat any other blobs,
        or if they should be eaten by another blob
        '''
        for other_blob_name in self.blobs.copy():
            other_blob = self.blobs[other_blob_name]

            if blob.is_bloblet and other_blob is blob.parent:
                # Our parent will eat us, don't try to eat them.
                continue


            # Can we eat them?
            elif math.dist(other_blob.pos, blob.pos) < blob.radius and blob.mass > other_blob.mass * self.parameters["blob_eat_ratio"]:
                # Yes we can
                other_blob.was_absorbed(blob)

            elif math.dist(other_blob.pos, blob.pos) < other_blob.radius and other_blob.mass > blob.mass * self.parameters["blob_eat_ratio"]:
                # They can eat us
                blob.was_absorbed(other_blob)

                # our blob is dead don't bother checking others
                break

            else:
                # Nobody can eat the other so just pass
                pass


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
        blobs_out = ""
        for i in self.blobs:
            blobs_out += f"{i}:{str(self.blobs[i])},"


        # now append the dot_list
        # This returns list of coords of every dot
        # ! It just works don't touch
        dots_out = str([a for sector in self.sectors for a in self.sectors[sector]])


        # now add parameters
        # These are the parameters we need to share with new player
        mp_params = (
            "world_width", "world_height", "random_seed", "random_count",
            "dot_mass", "blob_eat_ratio", "min_split_mass"
        )

        params_out = {i:self.parameters[i] for i in mp_params}
        params_out = str(params_out)

        out = [blobs_out, dots_out, params_out]

        print("[GAME]:Generated new intro packet")

        return out


    def data_to_send(self):
        '''
        Generate data to send to the server when we update something
        Data is new mass and score of player blob, and location
        '''
        out = f"{self.MY_ID},{self.player.mass},{self.player.score},"    # our id, our mass, our score
        out += f"{self.player.pos[0]},{self.player.pos[1]}" # our x, our y

        for bloblet in self.player.sub_blobs.copy():
            out += self.separator
            
            if bloblet.is_dead:
                out += f"{bloblet.id},{self.null_mass}, , "
                self.player.sub_blobs.remove(bloblet)
            else:
                out += f"{bloblet.id},{bloblet.mass},{bloblet.pos[0]},{bloblet.pos[1]}"

        return out


    def process_player_move(self, data):
        '''
        Process an update for movement of a player blob
        I.E. receiving end of data sent via above method
        '''
        foreign_blobs = data.split(self.separator)

        # Transform main player data
        try:
            blob, mass, score, pos_x, pos_y = foreign_blobs[0].split(",")

        except ValueError: # Some sort of transmission error occured, just move on
            return

        pos = (int(float(pos_x)), int(float(pos_y)))
        mass = int(mass)
        score = int(score)

        # Use data to calibrate blob
        self.blobs[blob].set_mass(mass)
        self.blobs[blob].set_score(score)
        self.blobs[blob].place(pos)


        # * Deal with player's bloblets
        for bloblet_data in foreign_blobs[1:]:
            info = bloblet_data.split(",")
            name = info[0]

            if int(info[1]) == self.null_mass:
                # Bloblet died, get rid of them
                self.disconnect_blob(name)

            elif name in self.blobs:
                # Bloblet is still alive, and we know about it
                mass, pos_x, pos_y = info[1:]
                pos = (int(float(pos_x)), int(float(pos_y)))
                mass = int(mass)

                # Use data to calibrate blob
                self.blobs[name].set_mass(mass)
                self.blobs[name].place(pos)

            else:
                # Create record for bloblet
                pos = (int(float(pos_x)), int(float(pos_y)))
                mass = int(mass)
                new_child = sub_cell(self.blobs[blob], mass)
                new_child.id = name
                new_child.set_name(blob)
                self.blobs[name] = new_child

                # Assign to parent
                self.blobs[blob].sub_blobs.add(new_child)

                # Use data to calibrate blob
                self.blobs[name].place(pos)


    def update_ui_elements(self):
        '''
        Periodically update UI elements
        Threaded to improve performance as we have to delete and redraw elements every time
        '''

        self.running_flag.wait()

        while self.running_flag.isSet():

            # * Keep player stats up to date
            player_text = f"Player stats:<br>Current Score - {self.player.score}<br>Peak Score - {self.player.peak_score}<br>Bloblet count - {len(self.player.sub_blobs)}<br>"
            self.ui_player_stats.kill()
            self.ui_player_stats = pygame_gui.elements.UITextBox(
                relative_rect=self.player_stats_rect,
                html_text=player_text,
                manager=self.ui_manager)


            # * Update Game overall stats

            total_game_mass = sum([self.blobs[blob].mass for blob in self.blobs])
            total_dot_mass = self.parameters["dot_mass"] * sum([len(self.sectors[sector]) for sector in self.sectors])

            self.ui_game_stats.kill()
            self.ui_game_stats = pygame_gui.elements.UITextBox(
                relative_rect=self.game_stats_rect,
                html_text=f"Total Mass of Blobs - {total_game_mass}<br>Mass of Live Dots - {total_dot_mass}",
                manager=self.ui_manager)

        
            # * Create Leaderboard
            # Get players names and their scores
            blobs_with_scores = [(self.blobs[blob].score, self.blobs[blob].name) for blob in self.blobs if not self.blobs[blob].is_bloblet]
            # Sort based on score
            blobs_with_scores.sort(key=lambda x: x[0])

            # Merge scores and name into a string
            for i, value in enumerate(blobs_with_scores):
                blobs_with_scores[i] = " - ".join((str(value[0]), value[1]))

            blobs_with_scores.reverse()

            # We need 9 people on the board
            while len(blobs_with_scores) < 9:
                blobs_with_scores.append("None - None")
            
            leaderboard_text = "<br>".join(blobs_with_scores[:9])
            self.ui_leaderboard.kill()
            self.ui_leaderboard = pygame_gui.elements.UITextBox(
                relative_rect=self.leaderboard_rect,
                html_text=f"Leaderboard:<br>{leaderboard_text}",
                manager=self.ui_manager)


            # * Display misc data
            if self.is_multiplayer:
                # Display our multiplayer info
                blob_count = len(self.blobs)     # [blob for blob in self.blobs if not blob.is_bloblet])
                
                self.ui_other_info.kill()
                self.ui_other_info = pygame_gui.elements.UITextBox(
                    relative_rect=self.other_info_rect,
                    html_text=f"Multiplayer Data:<br>Code - {self.host_name}<br>Blob count - {blob_count}<br>Port number - {self.port}",
                    manager=self.ui_manager)

                    # <br>You are the host - {self.host_name == self.MY_ID}

            else:
                # Display our AI info
                
                self.ui_other_info.kill()
                self.ui_other_info = pygame_gui.elements.UITextBox(
                    relative_rect=self.other_info_rect,
                    html_text=f"AI info:<br>Number of AI - {len(self.ai_blob_ids)}<br>Difficulty - {self.parameters['ai_difficulty']}",
                    manager=self.ui_manager)


            # Sleep to give time for things to change
            sleep(0.5)


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

        # Find width and height of screen in terms of sectors, rounded up
        # These are halved because we look from player's position in the centre of the screen
        # Add one to make sure dots are rendered at the edge of the screen
        screen_sector_width = (WORLD_WIDTH // self.parameters["sector_size"] + 1) // 2
        screen_sector_height = (WORLD_HEIGHT // self.parameters["sector_size"] + 1) // 2


        # Configure display and pygame settings
        self.game_display = pygame.display.set_mode(self.DISPLAY_GEOMETRY)
        self.game_display.fill((250, 250, 250))

        pygame.display.set_caption("Jario")


        clock = pygame.time.Clock()


        ## * Creating things!

        # Create PLayer
        player_start = (0, 0) #(- WORLD_WIDTH // 2, - WORLD_HEIGHT // 2)

        self.player = player_cell(self, player_start, self.parameters["player_colour"])
        self.player.set_name(self.parameters["player_name"])

        ##  Mouse Mode toggle will be in menu or something later
        mouse_mode = self.parameters["mouse_mode"]

        if mouse_mode:
            self.player.set_mouse_mode()


        self.blobs[self.MY_ID] = self.player
        print(f"[GAME]:Player {self.MY_ID} Created")
        # print(f"[GAME]:BLOBS LIST:{self.blobs}")

        # If we aren't multiplayer, we haven't yet configured our sectors or spawned dots
        if not self.sectors_configured:
            self.configure_sectors()

            dots_to_spawn = len(self.sectors) * 2 * self.parameters["dot_spawn_rate"]
            self.spawn_dots(dots_to_spawn)

        # Allow continuous dot spawning
        dot_spawn_thread = threading.Thread(target=self.continuous_dot_spawn)
        dot_spawn_thread.daemon = True
        dot_spawn_thread.start()


        # * Setup UI
        # Create UI manager
        self.ui_manager = pygame_gui.UIManager(self.DISPLAY_GEOMETRY)

        # Create UI pieces
        # The containing rectangles are seperated out else the function becomes too unwieldy
        self.player_stats_rect = pygame.Rect((int(self.DISPLAY_GEOMETRY[0] * 0.2), int(self.DISPLAY_GEOMETRY[1] * 0.8)),
                                            (int(self.DISPLAY_GEOMETRY[0] * 0.2), int(self.DISPLAY_GEOMETRY[1] * 0.15)))

        self.ui_player_stats = pygame_gui.elements.UITextBox(
            relative_rect=self.player_stats_rect,
            html_text="Loading Player Stats...",
            manager=self.ui_manager)


        self.game_stats_rect = pygame.Rect((int(self.DISPLAY_GEOMETRY[0] * 0.4), int(self.DISPLAY_GEOMETRY[1] * 0.8)),
                                            (int(self.DISPLAY_GEOMETRY[0] * 0.2), int(self.DISPLAY_GEOMETRY[1] * 0.15)))

        self.ui_game_stats = pygame_gui.elements.UITextBox(
            relative_rect=self.game_stats_rect,
            html_text='Loading Game Stats...',
            manager=self.ui_manager)


        self.other_info_rect = pygame.Rect((int(self.DISPLAY_GEOMETRY[0] * 0.6), int(self.DISPLAY_GEOMETRY[1] * 0.8)),
                                            (int(self.DISPLAY_GEOMETRY[0] * 0.2), int(self.DISPLAY_GEOMETRY[1] * 0.15)))

        self.ui_other_info = pygame_gui.elements.UITextBox(
            relative_rect=self.other_info_rect,
            html_text='Network_info',
            manager=self.ui_manager)


        self.leaderboard_rect = pygame.Rect((int(self.DISPLAY_GEOMETRY[0] * 0.8), int(self.DISPLAY_GEOMETRY[1] * 0.05)),
                                            (int(self.DISPLAY_GEOMETRY[0] * 0.15), int(self.DISPLAY_GEOMETRY[1] * 0.3)))

        self.ui_leaderboard = pygame_gui.elements.UITextBox(
            relative_rect=self.leaderboard_rect,
            html_text='Leaderboard',
            manager=self.ui_manager)

        
        # Create thread to periodically update UI elements
        ui_thread = threading.Thread(target=self.update_ui_elements)
        ui_thread.daemon = True
        ui_thread.start()

        self.running_flag.set()
        while self.running_flag.isSet():

            time_delta = clock.tick(self.UPS) / 1000


            # remove previous instances of everything
            self.game_display.fill((250, 250, 250))
            self.game_map.fill((0, 0, 0))

            for event in pygame.event.get():
                
                self.ui_manager.process_events(event)

                if event.type == pygame.QUIT:
                    print("[GAME]:Game Quit")

                    self.running_flag.clear()

                # if event.type == pygame.USEREVENT:
                #     if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                #         if event.ui_element == hello_button:
                #             print('Hello World!')


                # print(f"[GAME]:{event}")


            # * Debugging
            pressed_keys = pygame.key.get_pressed()

            if pressed_keys[pygame.K_UP]:
                self.player.eat(10)

            if pressed_keys[pygame.K_DOWN]:
                self.player.eat(-10)

            if pressed_keys[pygame.K_SPACE]:
                self.player.split()


            # * Move things
            # Move player
            self.player.move()
            
            for bloblet in self.player.sub_blobs:
                bloblet.move()

            # Move AI if present
            if not self.is_multiplayer:
                for ai in self.ai_blob_ids.copy():
                    self.blobs[ai].move()


            # * Eating time

            for blob_name in self.blobs:
                self.check_eat_food(self.blobs[blob_name])

            # See if our player can eat any other blobs
            self.check_eat_blob(self.player)

            # Let AIs eat each other or the player
            if not self.is_multiplayer:
                for ai in self.ai_blob_ids.copy():
                    try:
                        self.check_eat_blob(self.blobs[ai])
                    except KeyError:
                        # Blob we are about to check was eaten earlier this tick
                        continue

            # Player sub_blobs can eat each other and be eaten by player
            for sub_blob in self.player.sub_blobs.copy():
                if sub_blob.is_dead:
                    # Blob died in previous loop
                    continue

                # Let our player eat their sub_blobs
                if math.dist(self.player.pos, sub_blob.pos) < self.player.radius:
                    sub_blob.was_absorbed(self.player)

                else:
                    # Let sub_blobs eat each other
                    for other_blob in self.player.sub_blobs.copy():
                        if other_blob.is_dead:
                            # Blob died in previous loop
                            continue

                        elif other_blob is sub_blob:
                            # Don't eat yourself!
                            continue

                        elif math.dist(other_blob.pos, sub_blob.pos) < sub_blob.radius and sub_blob.mass > other_blob.mass * self.parameters["blob_eat_ratio"]:
                            # Good enough to eat!
                            other_blob.was_absorbed(sub_blob)



            # * DISPLAY THINGS

            # We need to render nearby dots
            player_sector_x = int(self.player.pos[0] // self.parameters["sector_size"])
            player_sector_y = int(self.player.pos[1] // self.parameters["sector_size"])

            # Look across the screen from our position
            # ! Make sure we don't exceed or undercut sector coords, i.e. reference negative coords
            if (min_x := player_sector_x - screen_sector_width) < 0:
                min_x = 0
            if (max_x := player_sector_x + screen_sector_width) > self.sectors_wide:
                max_x = self.sectors_wide

            if (min_y := player_sector_y - screen_sector_height) < 0:
                min_y = 0
            if (max_y := player_sector_y + screen_sector_height) > self.sectors_high:
                max_y = self.sectors_high

            # Start looking
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):

                    # Draw every dot in each sector
                    for dot in self.sectors[(x,y)]:

                        pygame.draw.circle(self.game_map, dot[2], (dot[0], dot[1]), self.parameters["dot_radius"], self.parameters["dot_radius"])


            # Display blobs
            for blob_name in self.blobs:
                if not self.blobs[blob_name].is_dead:
                    self.blobs[blob_name].display()


            # Update screen
            self.game_display.blit(self.game_map, self.player.camera_pos) # transfer game view to display

            # Display UI
            # Display here so it appears on top of the game
            self.ui_manager.draw_ui(self.game_display)
            self.ui_manager.update(time_delta)

            pygame.display.update()

        pygame.quit()
        print("[GAME]:PyGame has quit, game ended")

if __name__ == "__main__":

    print("[GAME]:MAIN")
    dummy_game = game()
    dummy_game.run()