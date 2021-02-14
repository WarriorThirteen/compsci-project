import math
import random
import threading

from time import sleep

try:
    from resources import game as gm
except ModuleNotFoundError:
    import game as gm


class ai_game(gm.game):
    '''
    Game to be run with AI
    '''
    def __init__(self, params={}):
        # Initialise things
        super().__init__(params)

        self.ai_respawn_time = 2

        # Create AI
        for _ in range(self.parameters["ai_limit"]):
            self.create_ai(self.parameters["ai_difficulty"])

        # Start continuous respawn
        ai_respawn_thread = threading.Thread(target=self.respawn_ai)
        ai_respawn_thread.daemon = True
        ai_respawn_thread.start()


    def create_ai(self, difficulty):
        '''
        Create an AI of the given difficulty level
        '''
        ai_id = str(random.randint(0, 100))

        start_pos = (random.randint(0, self.parameters["world_width"]), random.randint(0, self.parameters["world_width"]))
        colour = (random.randint(10, 255), random.randint(10, 255), random.randint(10, 255))
        start_mass = random.randint(400, 1000)

        if difficulty == 0:
            self.blobs[ai_id] = very_easy_ai(self, start_pos, colour, start_mass)

        elif difficulty == 1:
            self.blobs[ai_id] = easy_ai(self, start_pos, colour, start_mass)


        self.blobs[ai_id].id = ai_id
        self.ai_blob_ids.add(ai_id)

        print(f"[AI]:Created AI of difficulty {difficulty}, ID: {ai_id}")


    def respawn_ai(self):
        '''
        Continuously respawn blobs
        '''
        print("[AI]:Continuous AI respawn enabled")
        self.running_flag.wait()
        print("[AI]:AIs now respawning")

        while self.running_flag.isSet():

            # Not enough AI blobs AND only spawn new 5% of the time
            if len(self.ai_blob_ids) < self.parameters["ai_limit"] and random.random() <= 0.25:
                self.create_ai(self.parameters["ai_difficulty"])

            sleep(self.ai_respawn_time)


class ai_cell(gm.cell):
    '''
    Base AI class for AI types to subclass
    '''
    def __init__(self, *args):
        super().__init__(*args)

        self.set_name(gen_name())

        # Create random movement direction
        self.angle = (random.random() * 2 * math.pi) - math.pi

        # Set CCD -  Chance to Change Direction
        # This lets us continue in a direction for sufficient time to prevent wobbling
        self.ccd = 0.05

        # How many sectors we can see in each direction
        self.view_range = 2
    

    def angle_move(self, angle):
        '''
        Move ourselves in a direction denoted by the provided angle
        '''
        # Find ratio of x to y movement that we need
        self.d_x = self.speed * math.cos(angle)
        self.d_y = self.speed * math.sin(angle)

        # Move
        self.pos = [self.pos[0] + self.d_x, self.pos[1] + self.d_y]

        # Don't go through the walls
        self.wall_detect()


    def find_sectors(self):
        '''
        Returns a tuple of the coordinates of sectors visible to this blob:
        ((x1, y1), (x2, y2), etc)
        This excludes not real sectors off the edge of the map,
        and excludes the sector the blob is in
        '''
        out = []

        # Find our sector coords:
        sector_x, sector_y = self.pos[0] // self.game.parameters["sector_size"], self.pos[0] // self.game.parameters["sector_size"]

        # Determine max and min sector coords to check
        # Make sure we don't exceed or undercut sector coords, i.e. reference negative coords
        if (min_x := sector_x - self.view_range) < 0:
            min_x = 0
        if (max_x := sector_x + self.view_range) > self.game.sectors_wide:
            max_x = self.game.sectors_wide

        if (min_y := sector_y - self.view_range) < 0:
            min_y = 0
        if (max_y := sector_y + self.view_range) > self.game.sectors_high:
            max_y = self.game.sectors_high

        # Get coords
        for x in range(int(min_x), int(max_x) + 1):
            for y in range(int(min_y), int(max_y) + 1):
                if x == sector_x and y == sector_y:
                    continue
                out.append((x, y))

        return tuple(out)

    
    def was_absorbed(self, blob):
        '''
        We have died,
        Add mass to blob which ate us.
        Polymorphed to allow AI blobs to be removed from the ai_blob list
        '''
        super().was_absorbed(blob)
        self.game.ai_blob_ids.remove(self.id)
        print(f"[AI]:AI blob ID {self.id} has died")


    def move(self):
        '''
        Move the cell in the direction of it's choice, determined by the "angle" attribute.
        This is randomly changed, with frequency dependent on ccd attribute
        '''
        if random.random() <= self.ccd:
            self.change_angle()
        
        self.angle_move(self.angle)


class very_easy_ai(ai_cell):
    '''
    Easiest AI difficulty, moves randomly, changing direction 5% of the time
    '''
    def change_angle(self):
        '''
        Move based on our internal AI model
        This AI moves randomly
        '''
        self.angle = (random.random() * 2 * math.pi) - math.pi


class easy_ai(ai_cell):
    '''
    Simple, easy AI difficulty, which only moves towards the nearby sector with the highest concentration of dots
    '''
    def change_angle(self):
        '''
        Change our angle of travel
        '''
        max_dots = -1
        target_sector = (0,0)

        for sector in self.find_sectors():
            if (num_dots := len(self.game.sectors[sector])) > max_dots:
                # New highest mass sector, go here
                target_sector = sector
                max_dots = num_dots


        # Find real coords of target sector
        target_coords = [coord * self.game.parameters["sector_size"] for coord in target_sector]

        if math.dist(target_coords, self.pos) < self.game.parameters["sector_size"] * 0.5:
            # We are in or near this sector, move SouthEast to eat dots
            self.angle_move(0)

        else:
            # Go towards the sector
            # Find angle to get to this location
            rel_x = target_coords[0] - self.pos[0]
            rel_y = target_coords[1] - self.pos[1]

            self.angle = math.atan2(rel_y, rel_x)


gen_name = lambda: "AI"


if __name__ == "__main__":
    game = ai_game()
    game.run()