import pygame
import math


class cell:
    def __init__(self, display, pos=(0, 0), colour=(0, 0, 0), starting_mass=50):
        self.pos = [pos[0], pos[1]]
        self.colour = colour
        self.mass = starting_mass
        self.display_surface = display

        self.speed = 1 # for testing - will be a function later


    def display(self):
        pygame.draw.circle(self.display_surface, self.colour, self.pos, self.mass, self.mass)





class player_cell(cell):
    def __init__(self, *args):
        super().__init__(*args)
        self.d_x = 0
        self.d_y = 0
        self.mouse_pos = self.pos


    def update_direction(self):
        # current issue is speed decreases with distance from mouse 
        self.mouse_pos = pygame.mouse.get_pos()


        rel_x = self.mouse_pos[0] - self.pos[0]
        rel_y = self.mouse_pos[1] - self.pos[1]

        angle = math.atan2(rel_y, rel_x)

        self.d_x = self.speed * math.cos(angle)
        self.d_y = self.speed * math.sin(angle)


        # print(math.sqrt(rel_x ** 2 + rel_y ** 2))


    def move(self):
        self.update_direction()


        self.pos = [self.pos[0] + self.d_x, self.pos[1] + self.d_y]



        # Prevent wiggling about the cursor caused my over movement
        if abs(self.pos[0] - self.mouse_pos[0]) <= abs(self.d_x):
            self.pos[0] = self.mouse_pos[0]


        if abs(self.pos[1] - self.mouse_pos[1]) <= abs(self.d_y):
            self.pos[1] = self.mouse_pos[1]

        






##  Key Variables
pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
UPS = 30    # updates per second
SCREEN_GEOMETRY = (SCREEN_WIDTH, SCREEN_HEIGHT)




##  configure display and pygame settings
game_display = pygame.display.set_mode(SCREEN_GEOMETRY)
game_display.fill((250, 250, 250))

pygame.display.set_caption("Jario")


clock = pygame.time.Clock()


# Create stuff


PLAYER_CENTRE = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)



player_colour = (155, 0, 0)

player = player_cell(game_display, PLAYER_CENTRE, player_colour)


alive = True

while alive:
    # remove previous instances of everything
    game_display.fill((250, 250, 250))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            alive = False

        # elif event.type == pygame.MOUSEMOTION:
        #     player.update_direction()

        print(event)





    # Move things
    player.move()

    # display things
    player.display()

    # Update screen
    pygame.display.update()
    clock.tick()
