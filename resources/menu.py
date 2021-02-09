import tkinter as tk
import tkfontchooser as tkFont
import tkinter.colorchooser as tkcc



##  FUNCTIONS  ##

def not_implemented():
    '''
    Placeholder function to provide for not yet implemented buttons
    This allows quick searching of the document for incomplete functions
    '''
    not_implemented_text = "This function has not been implemented yet"

    # alert(not_implemented_text, root)
    print(not_implemented_text)


def make_alert_func(root):
    def alert(text):
        '''
        Create a small tktoplevel window to present an alert
        '''
        alert_window = tk.Toplevel(root)
        alert_window.minsize(200, 200)

        alert_window.title("Alert")
        tk.Label(alert_window, text=text).pack()

    return alert








class menus:
    def __init__(self,
        game_run_function=not_implemented,
        multiplayer_run_function=not_implemented,
        multiplayer_join_function=not_implemented,
        name_gen_function=lambda : "Jad",
        difficulty_options_list=("Very Easy", "Easy", "Medium", "Hard", "Very Hard", "Custom"),
        dot_spawn_rate=20, ai_limit=20):



        self.WINDOW_WIDTH = 1280     # These can be changed, but convenient for 720p to be used for
        self.WINDOW_HEIGHT = 720     # reasons mentioned in design


        self.WINDOW_BACKGROUND = "#FFF8C0" # New Yellow pand background


        self.FONT_FAMILY = "Small Fonts"  # Switch to pixel graphics if time allows
        # self.FONT_FAMILY = "Wingdings"

        self.run_game = game_run_function    # to switch to pygame to play the game
        self.run_mp_game = multiplayer_run_function
        self.join_mp_game = multiplayer_join_function

        self.difficulty_options = difficulty_options_list
        self.gen_name = name_gen_function
        self.max_spawn_rate = dot_spawn_rate # max spawn rate of dots
        self.max_ai_count = ai_limit

        # required length of multiplayer game join code
        self.JOIN_CODE_LENGTH = 3


        # Tracking for buttons and menus
        self.sound_on = True

        self.opened_home = False
        self.opened_sp = False
        self.opened_mp = False



        ##  Create and display menu

        self.root = tk.Tk()
        self.root.title("Jario")
        self.root.geometry(f"{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}")
        self.root.configure(bg=self.WINDOW_BACKGROUND)

        self.difficulty = tk.StringVar()
        self.difficulty.set(self.difficulty_options[1])  # default difficulty

        self.std_font = tkFont.Font(root=self.root, family=self.FONT_FAMILY, size=12)
        self.large_font = tkFont.Font(root=self.root, family=self.FONT_FAMILY, size=20)

        self.player_colour = "red"


        self.alert = make_alert_func(self.root)





        ##  Create sp menu and mp menu frames here

        ##  this means we can use pack_forget to close them on opening the home menu
        ##  even if we haven't been to the relevant menu before

        self.sp_menu_frame = tk.Frame(self.root, bg=self.WINDOW_BACKGROUND)
        self.mp_menu_frame = tk.Frame(self.root, bg=self.WINDOW_BACKGROUND)
        self.home_menu_frame = tk.Frame(self.root, bg=self.WINDOW_BACKGROUND)




        ##  Acquire images
        self.unmuted_icon = tk.PhotoImage(file="resources/images/menu_images/mute_icon.png")
        self.muted_icon = tk.PhotoImage(file="resources/images/menu_images/mute_icon_muted.png")
        self.cross_icon = tk.PhotoImage(file="resources/images/menu_images/cross_icon.png")
        self.back_icon = tk.PhotoImage(file="resources/images/menu_images/back_icon.png")

        self.title_image = tk.PhotoImage(file="resources/images/menu_images/title.png")
        self.play_image = tk.PhotoImage(file="resources/images/menu_images/play.png")

        #  Create Background
        self.bg_image = tk.PhotoImage(file="resources/images/menu_images/background3.png")


    ## Button Functions

    # opening menus
    def open_home_menu(self):
        self.sp_menu_frame.pack_forget()
        self.mp_menu_frame.pack_forget()

        if not self.opened_home:

            ##  Main Menu screen

            # Background
            home_bg_label = tk.Label(self.home_menu_frame, image=self.bg_image, bg=self.WINDOW_BACKGROUND)
            home_bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)


            # https://textcraft.net/
            title = tk.Label(self.home_menu_frame, image=self.title_image, bg=self.WINDOW_BACKGROUND)
            title.place(relx=0.5, rely=0.125, anchor="n")



            ##  Singleplayer and multiplayer buttons

            self.btn_singleplayer = tk.Button(self.home_menu_frame, command=self.open_singleplayer_menu, text="Single Player", font=self.large_font)
            self.btn_singleplayer.place(relx=0.2, rely=0.5, relwidth=0.2, relheight=0.15, anchor="w")

            self.btn_multiplayer = tk.Button(self.home_menu_frame, command=self.open_multiplayer_menu, text="Multiplayer", font=self.large_font)
            self.btn_multiplayer.place(relx=0.6, rely=0.5, relwidth=0.2, relheight=0.15, anchor="w")


            ##  auxiliary buttons

            self.btn_sound_toggle = tk.Button(self.home_menu_frame, command=self.toggle_sound, image=self.unmuted_icon, border=0, bg=self.WINDOW_BACKGROUND)  # , border=0)
            self.btn_sound_toggle.place(relx=0.05, rely=0.1)

            self.btn_close_program = tk.Button(self.home_menu_frame, command=self.close_program, image=self.cross_icon, border=0, bg=self.WINDOW_BACKGROUND)  # , border=0)
            self.btn_close_program.place(relx=0.95, rely=0.1, anchor="ne")

            self.opened_home = True

        self.home_menu_frame.pack(fill="both", expand=True)


    def open_multiplayer_menu(self):
        '''
        Create and display multiplayer options menu
        '''
        self.home_menu_frame.pack_forget()


        if not self.opened_mp:

            ##  multiplayer menu screen


            # Background
            mp_bg_label = tk.Label(self.mp_menu_frame, image=self.bg_image, bg=self.WINDOW_BACKGROUND)
            mp_bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)




            self.btn_back = tk.Button(self.mp_menu_frame, command=self.open_home_menu, image=self.back_icon, border=0, bg=self.WINDOW_BACKGROUND)  # , border=0)
            self.btn_back.place(relx=0.95, rely=0.1, anchor="ne")



            ##  Connect to game
            connect_options = tk.Frame(self.mp_menu_frame, bd=5, relief="groove") #, bg="blue")
            connect_options.place(relx=0.2, rely=0.3, relwidth=0.2, relheight=0.4)

            # Host game
            btn_host = tk.Button(connect_options, command=self.run_mp_game, text="Host Game", font=self.large_font, bg="green")
            btn_host.grid(columnspan=2, sticky="nsew")


            # Provide join code
            tk.Label(connect_options, text="Input game code to connect to:", wrap=100, font=self.std_font).grid(row=1, column=0, sticky="nsew")


            self.join_code = tk.StringVar()
            self.join_code_input = tk.Entry(connect_options, textvariable=self.join_code)
            self.join_code_input.grid(row=1, column=1, sticky="nsew")


            # Connect to hosted game by provided code
            btn_connect = tk.Button(connect_options, command=self.join_mp_game_holder, text="Join Game", font=self.large_font, bg="green")
            btn_connect.grid(row=2, columnspan=2, sticky="nsew")


            ##  Allow widgets to resize themselves
            connect_options.columnconfigure(0, weight=1)
            connect_options.columnconfigure(1, weight=1)

            connect_options.rowconfigure(0, weight=2)  # play button should be slightly larger than options
            connect_options.rowconfigure(1, weight=1)
            connect_options.rowconfigure(2, weight=2)




            # Options for user to customise themselves or their blob before hosting/connecting

            join_options_count = 0

            join_options = tk.Frame(self.mp_menu_frame, bd=5, relief="groove") #, bg="yellow")
            join_options.place(relx=0.8, rely=0.3, relwidth=0.2, relheight=0.4, anchor="ne")


            # Configure game

            tk.Label(join_options, text="Configure Game. PLACEHOLDER OPTIONS", wrap=200, font=self.std_font).grid(row=0, columnspan=2, sticky="nsew")


            # difficulty
            tk.Label(join_options, text="Difficulty", font=self.std_font).grid(row=1, column=0, sticky="nsew")

            self.difficulty_option_selector = tk.OptionMenu(join_options, self.difficulty, *self.difficulty_options)
            self.difficulty_option_selector.grid(row=1, column=1, sticky="nsew")

            join_options_count += 1

            # name
            # allow name to be retrieved elsewhere
            tk.Label(join_options, text="Name:", font=self.std_font).grid(row=2, column=0, sticky="nsew")

            self.name_input = tk.Entry(join_options)
            self.name_input.grid(row=2, column=1, sticky="nsew")
            self.name_input.insert(0, self.gen_name())

            join_options_count += 1

            # set colour
            tk.Label(join_options, text="Colour:", font=self.std_font).grid(row=3, column=0, sticky="nsew")

            self.colour_input = tk.Button(join_options, command=self.change_colour, text="Select Colour!", font=self.std_font, bg=self.player_colour)
            self.colour_input.grid(row=3, column=1, sticky="nsew")

            join_options_count += 1


            ##  Allow widgets to resize themselves
            join_options.columnconfigure(0, weight=1)
            join_options.columnconfigure(1, weight=1)

            join_options.rowconfigure(0, weight=2)  # play button should be slightly larger than options

            for i in range(1, join_options_count + 1):
                join_options.rowconfigure(i, weight=1)


            self.opened_mp = True

        self.mp_menu_frame.pack(fill="both", expand=True)


    def open_singleplayer_menu(self):
        '''
        Create and display single player options menu
        '''
        self.home_menu_frame.pack_forget()


        if not self.opened_sp:

            ##  single player menu screen

            # Background
            sp_bg_label = tk.Label(self.sp_menu_frame, image=self.bg_image, bg=self.WINDOW_BACKGROUND)
            sp_bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)



            btn_back = tk.Button(self.sp_menu_frame, command=self.open_home_menu, image=self.back_icon, border=0, bg=self.WINDOW_BACKGROUND)  # , border=0)
            btn_back.place(relx=0.95, rely=0.1, anchor="ne")


            ##  simple options
            simple_options_count = 0    # how many simple options there are, for resizing

            sp_simple_options = tk.Frame(self.sp_menu_frame, bd=5, relief="groove") #, bg="white")
            sp_simple_options.place(relx=0.2, rely=0.3, relwidth=0.2, relheight=0.4)


            # btn_play = tk.Button(sp_simple_options, command=self.run_game, text="PLAY", font=self.large_font, bg="green")
            btn_play = tk.Button(sp_simple_options, command=self.run_game, image=self.play_image, bg=self.WINDOW_BACKGROUND)
            btn_play.grid(columnspan=2, sticky="nsew")

            # simple option widgets go here
            
            # difficulty
            tk.Label(sp_simple_options, text="Difficulty", font=self.std_font).grid(row=1, column=0, sticky="nsew")

            self.difficulty_option_selector = tk.OptionMenu(sp_simple_options, self.difficulty, *self.difficulty_options)
            self.difficulty_option_selector.grid(row=1, column=1, sticky="nsew")

            simple_options_count += 1

            # name
            # allow name to be retrieved elsewhere
            tk.Label(sp_simple_options, text="Name:", font=self.std_font).grid(row=2, column=0, sticky="nsew")

            self.name_input = tk.Entry(sp_simple_options)
            self.name_input.grid(row=2, column=1, sticky="nsew")
            self.name_input.insert(0, self.gen_name())

            simple_options_count += 1

            # set colour
            tk.Label(sp_simple_options, text="Colour:", font=self.std_font).grid(row=3, column=0, sticky="nsew")

            self.colour_input = tk.Button(sp_simple_options, command=self.change_colour, text="Select Colour!", font=self.std_font, bg=self.player_colour)
            self.colour_input.grid(row=3, column=1, sticky="nsew")

            simple_options_count += 1




            ##  Allow widgets to resize themselves
            sp_simple_options.columnconfigure(0, weight=1)
            sp_simple_options.columnconfigure(1, weight=1)

            sp_simple_options.rowconfigure(0, weight=2)  # play button should be slightly larger than options

            for i in range(1, simple_options_count + 1):
                sp_simple_options.rowconfigure(i, weight=1)




            ## advanced options
            advanced_options_count = 0

            sp_advanced_options = tk.Frame(self.sp_menu_frame, bd=5, relief="groove") #, bg="white")
            sp_advanced_options.place(relx=0.8, rely=0.3, relwidth=0.2, relheight=0.4, anchor="ne")


            tk.Label(sp_advanced_options, text="Please select custom difficulty for these settings to take effect. PLACEHOLDER OPTIONS", wrap=200, font=self.std_font).grid(row=0, column=0, columnspan=2, sticky="nsew")
            advanced_options_count += 1

            # advanced option widgets go here
            # This will be populated as the actual game is made so it can be filled with relevant settings


            # dot spawn rate
            tk.Label(sp_advanced_options, text="Dot Spawn Rate:", font=self.std_font).grid(row=1, column=0, sticky="nsew")

            self.spawn_rate_slider = tk.Scale(sp_advanced_options, from_=1, to=self.max_spawn_rate, orient="horizontal", font=self.std_font)
            self.spawn_rate_slider.grid(row=1, column=1, sticky="nsew")

            advanced_options_count += 1



            # AI spawn limit
            tk.Label(sp_advanced_options, text="AI spawn limit:", font=self.std_font).grid(row=2, column=0, sticky="nsew")

            self.ai_count_slider = tk.Scale(sp_advanced_options, from_=1, to=self.max_ai_count, orient="horizontal", font=self.std_font)
            self.ai_count_slider.grid(row=2, column=1, sticky="nsew")

            advanced_options_count += 1



            ##  Allow widgets to resize themselves
            sp_advanced_options.columnconfigure(0, weight=1)
            sp_advanced_options.columnconfigure(1, weight=1)


            for i in range(advanced_options_count + 1):
                sp_advanced_options.rowconfigure(i, weight=1)



            self.opened_sp = True

        self.sp_menu_frame.pack(fill="both", expand=True)



    # Auxiliary Functions

    def change_colour(self):
        '''
        Change the selected colour and update the colour of the button for clarity
        '''
        self.player_colour = tkcc.askcolor()[1]
        self.colour_input.configure(bg=self.player_colour)
        print(self.player_colour)



    def get_spawn_rate(self):
        '''
        Get Spawn rate of dots set by the user
        '''
        return self.spawn_rate_slider.get()



    def get_join_code(self):
        '''
        Return code entered by user to join multiplayer game
        '''
        code = self.join_code.get()
        if len(code) > self.JOIN_CODE_LENGTH:
            self.alert("This code is the wrong length!")
        else:
            return "192.168.0." + code


    def join_mp_game_holder(self):
        '''
        Retreive code and attempt to the relevant multiplayer game
        '''
        code = self.get_join_code()
        if code == None:
            self.alert("Attempt to join failed")
        else:
            self.join_mp_game(code)


    def toggle_sound(self):
        if self.sound_on:
            self.btn_sound_toggle.config(image=self.muted_icon)
            self.sound_on = False

        else:
            self.btn_sound_toggle.config(image=self.unmuted_icon)
            self.sound_on = True

        self.alert("Sound isn't on anyway!")


    @staticmethod
    def close_program():
        exit()




if __name__ == "__main__":

    a = menus()

    a.open_home_menu()

    a.root.mainloop()