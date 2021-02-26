import random
from resources import menu, game, multiplayer, ai


##  Functions

def run_game():
	'''
    Called from within menu to close the tkinter menu and run pygame
    '''
	# game.game(main_menu.get_parameters()).run()
	ai.gen_name = gen_name
	ai.ai_game(main_menu.get_parameters()).run()


def run_multiplayer():
	'''
	Called from within menu to close the tkinter menu and run pygame in multiplayer mode, and host a game
	'''
	multiplayer.game = game.game(main_menu.get_parameters())
	multiplayer.PORT, multiplayer.game.port = main_menu.get_port(), main_menu.get_port()
	multiplayer.host()


def join_multiplayer(code):
	'''
    Called from within menu to close the tkinter menu and run pygame in multiplayer mode, and connect to a networked game
    '''
	multiplayer.game = game.game()
	multiplayer.PORT, multiplayer.game.port = main_menu.get_port(), main_menu.get_port()
	multiplayer.join(code)


def gen_name():
	'''
	Generate a random name for a blob
	'''
	with open("resources/other_data/names.txt", 'r') as file:
		name_list = file.readlines()
		name = random.choice(name_list)[:-1]
	return name


##  Variables
difficulty_options = (
	"Very Easy",
	"Easy"
	# "Medium",
	# "Hard",
	# "Very Hard",
	# "Custom"
)


##  Main program
main_menu = menu.menus(run_game, run_multiplayer, join_multiplayer, gen_name, difficulty_options)

main_menu.open_multiplayer_menu()
main_menu.open_singleplayer_menu()
main_menu.open_home_menu()


main_menu.root.mainloop()