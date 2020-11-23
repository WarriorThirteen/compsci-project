import random
from resources import menu


##  Functions

def run_game():
    '''
    Called from within menu to close the tkinter menu and run pygame
    '''
    menu.not_implemented()


def run_multiplayer():
    '''
    Called from within menu to close the tkinter menu and run pygame in multiplayer mode, and host a game
    '''
    menu.not_implemented()


def join_multiplayer():
    '''
    Called from within menu to close the tkinter menu and run pygame in multiplayer mode, and connect to a networked game
    '''
    menu.not_implemented()


def gen_name():
	'''
	Generate a random name for a blob
	'''
	with open("resources/other_data/names.txt", 'r') as file:
		name_list = file.readlines()
		name = name_list[random.randint(0, len(name_list))][:-1]
	return name


##  Variables
difficulty_options = (
	"Very Easy",
	"Easy",
	"Medium",
	"Hard",
	"Very Hard",
	"Custom"
)
max_dot_spawn_rate = 20 # temp until game has been tested with different values




##  Main program

menu.init(run_game, run_multiplayer, join_multiplayer, gen_name)
menu.open_home_menu()

menu.root.mainloop()

