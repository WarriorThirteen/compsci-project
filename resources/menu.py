# Menu verison 1

# https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAMAAN2rwQlUOEtUOFhRQzNLVkxRUFBVRkdPQ09WMVlKUy4u

## CHANGES FROM DESIGN
# Back to menu button on sp and mp menus
# No exit button at the bottom of the singleplayer options menu




import tkinter as tk
import tkfontchooser as tkFont
import tkinter.colorchooser as tkcc



def init(game_run_function,
    multiplayer_run_function=NotImplemented,
    multiplayer_join_function=NotImplemented,
    name_gen_function=lambda : "Jad",
    difficulty_options_list=("Very Easy", "Easy", "Medium", "Hard", "Very Hard", "Custom"),
    dot_spawn_rate=20, ai_limit=20
    ):
    

    ##  Variables
    global WINDOW_BACKGROUND   # Gray chosen in documentation

    global run_game
    global run_mp_game
    global join_mp_game

    global difficulty_options
    global gen_name
    global max_spawn_rate
    global max_ai_count


    WINDOW_WIDTH = 1280     # These can be changed, but convenient for 720p to be used for
    WINDOW_HEIGHT = 720     # reasons mentioned in design
 
    WINDOW_BACKGROUND = "#FAFAFA"   # Gray chosen in documentation
 
    # FONT_FAMILY = "Small Fonts"  # Switch to pixel graphics if time allows
    FONT_FAMILY = "MV Boli"

    run_game = game_run_function    # to switch to pygame to play the game
    run_mp_game = multiplayer_run_function
    join_mp_game = multiplayer_join_function

    difficulty_options = difficulty_options_list
    gen_name = name_gen_function
    max_spawn_rate = dot_spawn_rate # max spawn rate of dots
    max_ai_count = ai_limit



    global sound_on
 
    global opened_home
    global opened_sp
    global opened_mp

    sound_on = True
 
    opened_home = False
    opened_sp = False
    opened_mp = False




    ##  Create and display menu

    global root

    root = tk.Tk()
    root.title("Jario")
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    root.configure(bg=WINDOW_BACKGROUND)


    global difficulty
    global large_font
    global std_font
    global player_colour

    difficulty = tk.StringVar()
    difficulty.set(difficulty_options[1])  # default difficulty

    std_font = large_font = tkFont.Font(root=root, family=FONT_FAMILY, size=12)
    large_font = tkFont.Font(root=root, family=FONT_FAMILY, size=20)

    player_colour = "red"



    ##  Create sp menu and mp menu frames here

    ##  this means we can use pack_forget to close them on opening the home menu
    ##  even if we haven't been to the relevant menu before

    global sp_menu_frame
    global mp_menu_frame

    sp_menu_frame = tk.Frame(root, bg=WINDOW_BACKGROUND)
    mp_menu_frame = tk.Frame(root, bg=WINDOW_BACKGROUND)



    ##  Acquire images
    global unmuted_icon
    global muted_icon
    global cross_icon
    global back_icon

    unmuted_icon = tk.PhotoImage(file="resources/images/menu_images/mute_icon.png")
    muted_icon = tk.PhotoImage(file="resources/images/menu_images/mute_icon_muted.png")
    cross_icon = tk.PhotoImage(file="resources/images/menu_images/cross_icon.png")
    back_icon = tk.PhotoImage(file="resources/images/menu_images/back_icon.png")




def not_implemented():
    '''
    Placeholder function to provide for not yet implemented buttons
    This allows quick searching of the document for incomplete functions
    '''
    not_implemented_text = "This function has not been implemented yet"

    alert(not_implemented_text)
    print(not_implemented_text)



def alert(text):
    alert_window = tk.Toplevel(root)
    alert_window.minsize(200, 200)

    alert_window.title("Alert")
    tk.Label(alert_window, text=text).pack()




##  Button Functions

# opening menus
def open_home_menu():
    global opened_home

    global sp_menu_frame
    global mp_menu_frame
    sp_menu_frame.pack_forget()
    mp_menu_frame.pack_forget()

    if not opened_home:

        ##  Main Menu screen
        global home_menu_frame
        home_menu_frame = tk.Frame(root, bg=WINDOW_BACKGROUND)

        title = tk.Label(home_menu_frame, text="Jario", font=large_font, bg=WINDOW_BACKGROUND)
        title.place(relx=0.5, rely=0.125, anchor="n")


        ##  Singleplayer and multiplayer buttons

        global btn_singleplayer
        btn_singleplayer = tk.Button(home_menu_frame, command=open_singleplayer_menu, text="Single Player", font=large_font)
        btn_singleplayer.place(relx=0.2, rely=0.5, relwidth=0.2, relheight=0.15, anchor="w")

        global btn_multiplayer
        btn_multiplayer = tk.Button(home_menu_frame, command=open_multiplayer_menu, text="Multiplayer", font=large_font)
        btn_multiplayer.place(relx=0.6, rely=0.5, relwidth=0.2, relheight=0.15, anchor="w")



        ##  auxiliary buttons

        global btn_sound_toggle
        btn_sound_toggle = tk.Button(home_menu_frame, command=toggle_sound, image=unmuted_icon)
        btn_sound_toggle.place(relx=0.05, rely=0.1)

        global btn_close_program
        btn_close_program = tk.Button(home_menu_frame, command=close_program, image=cross_icon)
        btn_close_program.place(relx=0.95, rely=0.1, anchor="ne")

        opened_home = True

    home_menu_frame.pack(fill="both", expand=True)



def open_multiplayer_menu():
    '''
    Create and display multiplayer options menu
    '''
    home_menu_frame.pack_forget()

    global opened_mp
    global mp_menu_frame


    if not opened_mp:

        ##  multiplayer menu screen
        global run_mp_game
        global large_font
        global std_font

        global back_icon
        global difficulty_options
        global difficulty
        global player_colour

        btn_back = tk.Button(mp_menu_frame, command=open_home_menu, image=back_icon)
        btn_back.place(relx=0.95, rely=0.1, anchor="ne")



        ##  Connect to game
        connect_options = tk.Frame(mp_menu_frame, bd=5, relief="groove") #, bg="blue")
        connect_options.place(relx=0.2, rely=0.3, relwidth=0.2, relheight=0.4)

        # Host game
        btn_host = tk.Button(connect_options, command=run_mp_game, text="Host Game", font=large_font, bg="green")
        btn_host.grid(columnspan=2, sticky="nsew")


        # Provide join code
        tk.Label(connect_options, text="Input game code to connect to:", wrap=100, font=std_font).grid(row=1, column=0, sticky="nsew")

        global join_code
        join_code = tk.StringVar()
        join_code_input = tk.Entry(connect_options, textvariable=join_code)
        join_code_input.grid(row=1, column=1, sticky="nsew")


        # Connect to hosted game by provided code
        btn_connect = tk.Button(connect_options, command=run_mp_game, text="Join Game", font=large_font, bg="green")
        btn_connect.grid(row=2, columnspan=2, sticky="nsew")


        ##  Allow widgets to resize themselves
        connect_options.columnconfigure(0, weight=1)
        connect_options.columnconfigure(1, weight=1)

        connect_options.rowconfigure(0, weight=2)  # play button should be slightly larger than options
        connect_options.rowconfigure(1, weight=1)
        connect_options.rowconfigure(2, weight=2)






        # Options for user to customise themselves or their blob before hosting/connecting

        join_options_count = 0

        join_options = tk.Frame(mp_menu_frame, bd=5, relief="groove") #, bg="yellow")
        join_options.place(relx=0.8, rely=0.3, relwidth=0.2, relheight=0.4, anchor="ne")


        # Configure game

        tk.Label(join_options, text="Configure Game", font=std_font).grid(row=0, columnspan=2, sticky="nsew")

        # difficulty
        global difficulty_option_selector
        tk.Label(join_options, text="Difficulty", font=std_font).grid(row=1, column=0, sticky="nsew")
        difficulty_option_selector = tk.OptionMenu(join_options, difficulty, *difficulty_options)
        difficulty_option_selector.grid(row=1, column=1, sticky="nsew")
        join_options_count += 1

        # name
        global name_input   # allow name to be retrieved elsewhere
        tk.Label(join_options, text="Name:", font=std_font).grid(row=2, column=0, sticky="nsew")
        name_input = tk.Entry(join_options)
        name_input.grid(row=2, column=1, sticky="nsew")
        name_input.insert(0, gen_name())
        join_options_count += 1

        # set colour
        global colour_input
        tk.Label(join_options, text="Colour:", font=std_font).grid(row=3, column=0, sticky="nsew")
        colour_input = tk.Button(join_options, command=change_colour, text="Select Colour!", font=std_font, bg=player_colour)
        colour_input.grid(row=3, column=1, sticky="nsew")
        join_options_count += 1


        ##  Allow widgets to resize themselves
        join_options.columnconfigure(0, weight=1)
        join_options.columnconfigure(1, weight=1)

        join_options.rowconfigure(0, weight=2)  # play button should be slightly larger than options

        for i in range(1, join_options_count + 1):
            join_options.rowconfigure(i, weight=1)


        opened_mp = True

    mp_menu_frame.pack(fill="both", expand=True)




def open_singleplayer_menu():
    '''
    Create and display single player options menu
    '''
    home_menu_frame.pack_forget()

    global opened_sp
    global sp_menu_frame


    if not opened_sp:

        ##  single player menu screen
        global run_game
        global large_font
        global std_font

        global back_icon
        global difficulty_options
        global difficulty
        global player_colour

        btn_back = tk.Button(sp_menu_frame, command=open_home_menu, image=back_icon)
        btn_back.place(relx=0.95, rely=0.1, anchor="ne")



        ##  simple options
        simple_options_count = 0    # how many simple options there are, for resizing
        sp_simple_options = tk.Frame(sp_menu_frame, bd=5, relief="groove") #, bg="white")
        sp_simple_options.place(relx=0.2, rely=0.3, relwidth=0.2, relheight=0.4)


        btn_play = tk.Button(sp_simple_options, command=run_game, text="PLAY", font=large_font, bg="green")
        btn_play.grid(columnspan=2, sticky="nsew")

        # simple option widgets go here
        
        # difficulty
        global difficulty_option_selector
        tk.Label(sp_simple_options, text="Difficulty", font=std_font).grid(row=1, column=0, sticky="nsew")
        difficulty_option_selector = tk.OptionMenu(sp_simple_options, difficulty, *difficulty_options)
        difficulty_option_selector.grid(row=1, column=1, sticky="nsew")
        simple_options_count += 1

        # name
        global name_input   # allow name to be retrieved elsewhere
        tk.Label(sp_simple_options, text="Name:", font=std_font).grid(row=2, column=0, sticky="nsew")
        name_input = tk.Entry(sp_simple_options)
        name_input.grid(row=2, column=1, sticky="nsew")
        name_input.insert(0, gen_name())
        simple_options_count += 1

        # set colour
        global colour_input
        tk.Label(sp_simple_options, text="Colour:", font=std_font).grid(row=3, column=0, sticky="nsew")
        colour_input = tk.Button(sp_simple_options, command=change_colour, text="Select Colour!", font=std_font, bg=player_colour)
        colour_input.grid(row=3, column=1, sticky="nsew")
        simple_options_count += 1




        ##  Allow widgets to resize themselves
        sp_simple_options.columnconfigure(0, weight=1)
        sp_simple_options.columnconfigure(1, weight=1)

        sp_simple_options.rowconfigure(0, weight=2)  # play button should be slightly larger than options

        for i in range(1, simple_options_count + 1):
            sp_simple_options.rowconfigure(i, weight=1)




        ## advanced options
        advanced_options_count = 0

        sp_advanced_options = tk.Frame(sp_menu_frame, bd=5, relief="groove") #, bg="white")
        sp_advanced_options.place(relx=0.8, rely=0.3, relwidth=0.2, relheight=0.4, anchor="ne")


        tk.Label(sp_advanced_options, text="Please select custom difficulty for these settings to take effect", wrap=200, font=std_font).grid(row=0, column=0, columnspan=2, sticky="nsew")
        advanced_options_count += 1

        # advanced option widgets go here
        # This will be populated as the actual game is made so it can be filled with relevant settings


        # dot spawn rate
        global spawn_rate_slider
        global max_spawn_rate
        tk.Label(sp_advanced_options, text="Dot Spawn Rate:", font=std_font).grid(row=1, column=0, sticky="nsew")
        spawn_rate_slider = tk.Scale(sp_advanced_options, from_=1, to=max_spawn_rate, orient="horizontal", font=std_font)
        spawn_rate_slider.grid(row=1, column=1, sticky="nsew")
        advanced_options_count += 1



        # AI spawn limit
        global ai_count_slider
        global max_ai_count
        tk.Label(sp_advanced_options, text="AI spawn limit:", font=std_font).grid(row=2, column=0, sticky="nsew")
        ai_count_slider = tk.Scale(sp_advanced_options, from_=1, to=max_ai_count, orient="horizontal", font=std_font)
        ai_count_slider.grid(row=2, column=1, sticky="nsew")
        advanced_options_count += 1



        ##  Allow widgets to resize themselves
        sp_advanced_options.columnconfigure(0, weight=1)
        sp_advanced_options.columnconfigure(1, weight=1)


        for i in range(advanced_options_count + 1):
            sp_advanced_options.rowconfigure(i, weight=1)



        opened_sp = True

    sp_menu_frame.pack(fill="both", expand=True)




# Auxiliary Functions

def change_colour():
    '''
    Change the selected colour and update the colour of the button for clarity
    '''
    global player_colour
    global colour_input
    player_colour = tkcc.askcolor()[1]
    colour_input.configure(bg=player_colour)
    # print(colour)


def get_spawn_rate():
    '''
    Get Spawn rate of dots set by the user
    '''
    global spawn_rate_slider
    return spawn_rate_slider.get()


def get_join_code():
    '''
    Return code entered by user to join multiplayer game
    '''
    global join_code
    return join_code.get()



def toggle_sound():
    global sound_on
    if sound_on:
        btn_sound_toggle.config(image=muted_icon)
        sound_on = False

    else:
        btn_sound_toggle.config(image=unmuted_icon)
        sound_on = True

    not_implemented()


def close_program():
    exit()




if __name__ == "__main__":

    init(not_implemented)

    open_home_menu()

    root.mainloop()