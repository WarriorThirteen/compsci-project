import pygame
import math


class cell:
    def __init__(self, world, world_xy, pos=(0, 0), colour=(0, 0, 0), starting_mass=50):
        self.pos = [pos[0], pos[1]]
        self.colour = colour
        self.mass = starting_mass
        self.radius = starting_mass
        self.world_surface = world
        self.world_geometry = world_xy

        self.speed = 10 # for testing - will be a function later


    def display(self):
        pygame.draw.circle(self.world_surface, self.colour, self.pos, self.radius, self.radius)





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
        self.camera_pos = [ - self.pos[0] + self.display_geometry[0] // 2, - self.pos[1] + self.display_geometry[1] // 2]
        # self.camera_pos = [self.camera_pos[0] - self.d_x, self.camera_pos[1] - self.d_y]

        # Prevent wiggling about the cursor caused my over movement
        if abs(self.pos[0] - self.mouse_pos[0]) <= abs(self.d_x):
            self.pos[0] = self.mouse_pos[0]

        if abs(self.pos[1] - self.mouse_pos[1]) <= abs(self.d_y):
            self.pos[1] = self.mouse_pos[1]


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
        if (displacement := -self.pos[0]) > 0:
            self.pos[0] += displacement
            self.camera_pos[0] -= displacement

        if (displacement := -self.pos[1]) > 0:
            self.pos[1] += displacement
            self.camera_pos[1] -= displacement

        if (displacement := self.world_geometry[0] - self.pos[0] ) < 0 :
            self.pos[0] += displacement
            self.camera_pos[0] -= displacement

        if (displacement := self.world_geometry[1] - self.pos[1] ) < 0 :
            self.pos[1] += displacement
            self.camera_pos[1] -= displacement




    def translate(self, new_pos):
        '''
        simple quick translation for testing
        '''
        self.pos[0] += new_pos[0]
        self.pos[1] += new_pos[1]
        self.camera_pos[0] -= new_pos[0]
        self.camera_pos[1] -= new_pos[1]


def Main():

    ##  Key Variables
    pygame.init()

    DISPLAY_WIDTH = 1280
    DISPLAY_HEIGHT = 720
    DISPLAY_GEOMETRY = (DISPLAY_WIDTH, DISPLAY_HEIGHT)
    UPS = 60    # updates per second

    WORLD_WIDTH = 1000
    WORLD_HEIGHT = 1000
    WORLD_GEOMETRY = (WORLD_WIDTH, WORLD_HEIGHT)


    ##  Mouse Mode toggle will be in menu or something later
    mouse_mode = True



    ##  configure display and pygame settings
    game_display = pygame.display.set_mode(DISPLAY_GEOMETRY)
    game_display.fill((250, 250, 250))

    pygame.display.set_caption("Jario")


    clock = pygame.time.Clock()


    ##  Creating things!


    # Create world

    game_map = pygame.Surface(WORLD_GEOMETRY)


    # Create PLayer
    player_colour = (155, 0, 0)
    player_centre = (0, 0) #(- WORLD_WIDTH // 2, - WORLD_HEIGHT // 2)

    player = player_cell(DISPLAY_GEOMETRY, game_map, WORLD_GEOMETRY, player_centre, player_colour)

    if mouse_mode:
        player.set_mouse_mode()

    # player.translate((1000, 100))

    alive = True

    while alive:
        # remove previous instances of everything
        game_display.fill((250, 250, 250))
        game_map.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                alive = False


            print(event)



        # Move things
        player.move()

        # display things
        player.display()

        # Update screen
        game_display.blit(game_map, player.camera_pos) # transfer game view to display
        pygame.display.update()

        clock.tick(UPS)

if __name__ == "__main__":
    Main()