import random
from resources import menu, game, multiplayer


##  Functions

def run_game():
	'''
    Called from within menu to close the tkinter menu and run pygame
    '''
	game.game().run()


def run_multiplayer():
	'''
	Called from within menu to close the tkinter menu and run pygame in multiplayer mode, and host a game
	'''
	multiplayer.game = game.game()
	multiplayer.host()


def join_multiplayer(code):
	'''
    Called from within menu to close the tkinter menu and run pygame in multiplayer mode, and connect to a networked game
    '''
	multiplayer.game = game.game()
	multiplayer.join(code)


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
main_menu = menu.menus(run_game, run_multiplayer, join_multiplayer, gen_name)
main_menu.open_home_menu()

main_menu.root.mainloop()